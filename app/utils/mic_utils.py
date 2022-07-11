import datetime
import json
import os
import urllib.parse
from typing import List

import requests

from app.associations import ConnectionCalendar, CalendarEvent
from app.calendars.calendars import Calendar
from app.connections.connections import Connection
from app.constants import Constants
from app.events.events import Event
from app.exception import MicrosoftRequestError
from app.utils import dict_utils

mic_tenant_id = os.environ['MIC-DIRECTORY-ID']
mic_client_id = os.environ['MIC-CLIENT-ID']
mic_redirect_uri = os.environ['MIC-REDIRECT-URL']
mic_scopes = 'User.Read Calendars.ReadWrite offline_access'
mic_client_secret = os.environ['MIC-SECRET-VALUE']


def generate_url_login(state):
    params = {
        'client_id': mic_client_id,
        'response_type': 'code',
        'redirect_uri': mic_redirect_uri,
        'response_mode': 'query',
        'scope': mic_scopes,
        'state': state
    }
    return f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/authorize?' \
           f'{urllib.parse.urlencode(params)}'


def request_exchange_code(code):
    params = {
        'client_id': mic_client_id,
        'scope': mic_scopes,
        'code': code,
        'redirect_uri': mic_redirect_uri,
        'grant_type': 'authorization_code',
        'client_secret': mic_client_secret
    }

    response = requests.post(url=f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/token', data=params)
    return json.loads(response.text)


def refresh_token(credentials: dict):
    params = {
        'client_id': mic_client_id,
        'scope': mic_scopes,
        'refresh_token': credentials.get('refresh_token'),
        'redirect_uri': mic_redirect_uri,
        'grant_type': 'refresh_token',
        'client_secret': mic_client_secret
    }
    res = requests.post(url=f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/token', data=params)
    res_dict = json.loads(res.text)
    if 'refresh_token' not in res_dict:
        res_dict['refresh_token'] = credentials.get('refresh_token')
    return res_dict


def create_authorized_request(url: str, connection: Connection, method: str, deep=0, **kwargs) -> dict:
    credentials = connection.credentials
    headers = {"Authorization": f"Bearer {credentials.get('access_token')}",
               'Prefer': 'IdType="ImmutableId"',
               "Content-Type": "application/json"}
    match method:
        case Constants.POST_METHOD:
            res = requests.post(url, headers=headers, **kwargs)
        case Constants.GET_METHOD:
            res = requests.get(url, headers=headers, **kwargs)
        case Constants.PATCH_METHOD:
            res = requests.patch(url=url, headers=headers, **kwargs)
        case Constants.DELETE_METHOD:
            res = requests.delete(url=url, headers=headers, **kwargs)
        case _:
            raise ValueError(f'Method = {method} is invalid')
    if res.status_code == 401 and deep < 1:
        connection.credentials = refresh_token(credentials=connection.credentials)
        return create_authorized_request(url, connection, method=method, deep=1, **kwargs)
    if 200 <= res.status_code < 300:
        if res.text:
            return json.loads(res.text)
    else:
        raise requests.exceptions.HTTPError


def create_connection(credentials: dict) -> Connection:
    result = Connection()
    result.credentials = credentials
    response = create_authorized_request(Constants.MIC_PROFILE_URI, connection=Connection(credentials=credentials),
                                         method=Constants.GET_METHOD)
    payload = response.get('value')[0]
    result.type = Constants.ACCOUNT_TYPE_MICROSOFT
    result.platform_id = payload.get('id')
    result.username = f'{payload.get("givenName")} {payload.get("surname")}'
    result.email = payload.get('userPrincipalName')
    return result


def load_association_calendars_by_linked_account(connection: Connection) -> List[ConnectionCalendar]:
    res = create_authorized_request(url=Constants.MIC_CALENDARS_URI,
                                    connection=connection,
                                    method=Constants.GET_METHOD)
    result = []
    for item in res.get('value'):
        calendar = convert_to_calendar(item)
        association = ConnectionCalendar()
        association.calendar = calendar
        association.default_flag = item.get('isDefaultCalendar')
        access_role = Constants.ACCESS_ROLE_READ + f'{Constants.ACCESS_ROLE_WRITE if item.get("canEdit") else ""}' + \
                      f'{Constants.ACCESS_ROLE_SHARE if item.get("canShare") else ""}'
        if connection.email.__eq__(item.get('owner').get('address')):
            association.owner_flag = True
        else:
            association.owner_flag = False
        association.access_role = access_role
        result.append(association)
    return result


def convert_to_calendar(item: dict):
    calendar = Calendar()
    calendar.type = Constants.ACCOUNT_TYPE_MICROSOFT
    calendar.platform_id = item.get('id')
    calendar.summary = item.get('name')
    calendar.color_id = item.get('hexColor')
    calendar.foreground_color = calendar.background_color = item.get('color')
    calendar.created_by = item.get('owner')
    return calendar


def load_association_events_by_calendar(calendar: Calendar, connection: Connection) -> List[CalendarEvent]:
    res = create_authorized_request(url=Constants.MIC_GET_POST_EVENTS_BY_CALENDAR_URI.format(calendar.platform_id),
                                    connection=connection,
                                    method=Constants.GET_METHOD)
    result = []
    for item in res.get('value'):
        event = convert_to_event(item)
        association_event = CalendarEvent()
        association_event.owner_flag = item.get('isOrganizer')
        association_event.response_status = json.dumps(item.get('responseStatus'))
        association_event.event = event
        result.append(association_event)
    return result


def convert_to_event(item: dict) -> Event:
    event = Event()
    event.type = Constants.ACCOUNT_TYPE_MICROSOFT
    event.attendees = item.get('attendees')
    event.description = item.get('body').get('content')

    item.get('bodyPreview')
    event.summary = item.get('subject')

    event.end = item.get('end')
    event.guests_can_see_other_guests = item.get('hideAttendees')
    event.uid = item.get('iCalUId')
    event.platform_id = item.get('id')
    event.updated = item.get('lastModifiedDateTime')
    event.location = json.dumps(item.get('location'))
    # events.conference_data = item.get('onlineMeeting')
    event.organizer = item.get('organizer')
    event.html_link = item.get('webLink')
    event.status = item.get('showAs')
    event.start = item.get('start')
    event.recurring_event_id = item.get('seriesMasterId')
    event.visibility = item.get('sensitivity')
    event.recurrence = [json.dumps(item.get('recurrence'))]

    if item.get('isReminderOn'):
        event.reminders = [{'minutes': item.get('reminderMinutesBeforeStart')}]
    return event


def representation_event(event: Event) -> dict:
    result = {
        'attendees': event.attendees,
        'subject': event.summary,
        'end': event.end,
        'hideAttendees': event.guests_can_see_other_guests,
        'iCalUId': event.uid,
        'id': event.platform_id,
        'lastModifiedDateTime': event.updated,
        'location': event.location,
        'organizer': event.organizer,
        'webLink': event.html_link,
        'showAs': event.status,
        'start': event.start,
        'seriesMasterId': event.recurring_event_id,
        'sensitivity': event.visibility,
        'recurrence': representation_rrule(event.recurrence[0], event.start)
    }
    if event.description:
        result['body'] = {
            'content': event.description
        }
    return dict_utils.remove_empty_or_none(result)


def representation_calendar(calendar: Calendar) -> dict:
    result = {
        'name': calendar.summary
    }
    return dict_utils.remove_empty_or_none(result)


def create_calendar(calendar: Calendar, connection: Connection) -> Calendar:
    res = create_authorized_request(url=Constants.MIC_CALENDARS_URI,
                                    connection=connection,
                                    method=Constants.POST_METHOD,
                                    json=representation_calendar(calendar=calendar))
    return convert_to_calendar(res)


# def update_calendar(calendars: Calendar, connections: Connection) -> Calendar:
#     res = create_authorized_request(
#         url=Constants.GOOGLE_UPDATE_PATCH_CALENDAR_API_URL.format(calendar_id=calendars.platform_id),
#         users=connections,
#         method=Constants.PUT_METHOD,
#         data=representation_calendar(calendars=calendars)
#     )
#     return convert_to_calendar(res)


def delete_calendar(calendar: Calendar, connection: Connection) -> None:
    create_authorized_request(
        url=Constants.MIC_CALENDARS_URI + f'/{calendar.platform_id}',
        connection=connection,
        method=Constants.DELETE_METHOD
    )


def patch_calendar(calendar: Calendar, new_calendar: Calendar, connection: Connection) -> Calendar:
    res = create_authorized_request(
        url=Constants.MIC_CALENDARS_URI + f'/{calendar.platform_id}',
        connection=connection,
        method=Constants.PATCH_METHOD,
        json=representation_calendar(calendar=new_calendar))
    return convert_to_calendar(res)


def create_event(event: Event, calendar: Calendar, connection: Connection) -> Event:
    res = create_authorized_request(
        url=Constants.MIC_GET_POST_EVENTS_BY_CALENDAR_URI.format(calendar.platform_id),
        method=Constants.POST_METHOD,
        connection=connection,
        json=representation_event(event=event)
    )
    return convert_to_event(res)


mapping_day_of_week = {
    'SU': 'sunday',
    'MO': 'monday',
    'TU': 'tuesday',
    'WE': 'wednesday',
    'TH': 'thursday',
    'FR': 'friday',
    'SA': 'saturday'
}

mapping_index = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'last': 5
}


def representation_rrule(data: str, start: datetime.datetime):
    freq, interval, wkst, byday, bymonth, bymonthday, until, count = parser_rrule(data)

    recurrence_pattern = {'interval': interval, 'firstDayOfWeek': mapping_day_of_week[wkst]}

    if byday and byday.find(',') > 0:
        byday = list(byday.split(','))
        byday = [mapping_day_of_week[item] for item in byday]
    match freq:
        case 'DAILY':
            recurrence_pattern['type'] = 'daily'
        case 'WEEKLY':
            recurrence_pattern['daysOfWeek'] = byday
        case _:
            recurrence_pattern['month'] = bymonth
            if bymonthday:
                if freq.__eq__('YEARLY'):
                    # YEARLY
                    recurrence_pattern['type'] = 'absoluteYearly'
                else:
                    # MONTHLY
                    recurrence_pattern['type'] = 'absoluteMonthly'
                recurrence_pattern['dayOfMonth'] = bymonthday
            else:  # contain BYDAY
                byday = byday if len(byday) == 3 else f'1{byday}'
                if freq.__eq__('YEARLY'):
                    # YEARLY
                    recurrence_pattern['type'] = 'relativeYearly'
                else:
                    # MONTHLY
                    recurrence_pattern['type'] = 'relativeMonthly'
                recurrence_pattern['daysOfWeek'] = byday[1:]
                recurrence_pattern['index'] = byday[0:1]

    range = {}
    if until:
        range['type'] = 'endDate'
        range['endDate'] = until
    elif count:
        range['type'] = 'numbered'
        range['numberOfOccurrences'] = count
    else:
        range['type'] = 'noEnd'
    range['startDate'] = start.date().__str__()

    return {
        'pattern': recurrence_pattern,
        'range': range
    }


def parser_rrule(data: str):
    data = data[0]
    data = data.replace('RRULE:', '')
    data = list(data.split(';'))
    result = {}
    for item in data:
        split = list(item.split('='))
        result[split[0]] = split[1]
    freq = result.get('FREQ')
    interval = result.get('INTERVAL')
    wkst = result.get('WKST')
    byday = result.get('BYDAY')
    if byday and byday.find(',') > 0:
        byday = list(byday.split(','))
    bymonth = result.get('BYMONTH')
    bymonthday = result.get('BYMONTHDAY')
    until = result.get('UNTIL')
    count = result.get('COUNT')
    return freq, interval, wkst, byday, bymonth, bymonthday, until, count


def mic_recurrence_to_ical(data: dict):
    result = 'RRULE:FREQ='
    if data is None:
        return None
    else:
        pattern = data.get('pattern')
        range = data.get('range')
        index = pattern.get('index')
        freq = pattern.get('type')
        if freq.startswith('relative'):
            if freq.endswith('Yearly'):
                result += 'YEARLY;'
            else:
                result += 'MONTHLY;'
            result += f'BYMONTH={pattern.get("month")};' \
                      f'BYDAY={mapping_index.get(index) + pattern.get("daysOfWeek")[0][0:2].upper()};'
        elif freq.startswith('absolute'):
            if freq.endswith('Yearly'):
                result += 'YEARLY;'
            else:
                result += 'MONTHLY;'
            result += f'BYMONTH={pattern.get("month")};BYMONTHDAY={pattern.get("dayOfMonth")};'
        elif freq.__eq__('daily'):
            result += 'DAILY;'
        elif freq.__eq__('weekly'):
            result += f'WEEKLY;BYMONTHDAY={pattern.get("dayOfMonth")};'
        result += f'INTERVAL={pattern.get("interval")};'
        match range.get('type'):
            case 'endDate':
                result += f'UNTIL={range.get("endDate")};'
            case 'noEnd':
                pass
            case 'numbered':
                result += f'COUNT={range.get("numberOfOccurrences")};'
        result += f'WKST={pattern.get("firstDayOfWeek")[0:2].upper()}'
    return result
