import json
import os
import urllib.parse
import datetime
from typing import Union, List, Optional

import jwt
import requests

from app.account.account import Account
from app.association import ConnectionCalendar, CalendarEvent
from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.constants import Constants
from app.event.event import Event
from app.utils import dict_utils

client_id = os.environ['GG-CLIENT-ID']
client_secret = os.environ['GG-CLIENT-SECRET']
redirect_uri = os.environ['GG-LOGIN-REDIRECT']
redirect_uri_connection = os.environ['GG-CONNECTION-REDIRECT']
scopes_connection = os.environ['GG-CONNECT-SCOPES']
scopes_login = os.environ['GG-LOGIN-SCOPES']


def create_authorized_request(url: str, account: Union[Account, Connection], method: str, deep=0, **kwargs) -> Optional[dict]:
    credentials = account.credentials
    headers = {"Authorization": f"Bearer {credentials.get('access_token')}",
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
        case Constants.PUT_METHOD:
            res = requests.put(url=url, headers=headers, **kwargs)
        case _:
            raise ValueError('Method is invalid')
    if res.status_code == 401 and deep < 1:
        account.credentials = refresh_token(credentials=account.credentials)
        return create_authorized_request(url, account, method=method, deep=1, **kwargs)
    if 200 <= res.status_code < 300:
        if res.text:
            return json.loads(res.text)
    else:
        raise requests.exceptions.HTTPError


def refresh_token(credentials: dict):
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': credentials.get('refresh_token'),
        'grant_type': 'refresh_token'
    }
    res = requests.post(url=Constants.GOOGLE_AUTHORIZATION_SERVER_URL + 'token', data=params)
    res_dict = json.loads(res.text)
    if 'refresh_token' not in res_dict:
        res_dict['refresh_token'] = credentials.get('refresh_token')
    return res_dict


def generate_url_login(state=None, connect_calendar=False):
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'include_granted_scopes': 'true',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    if state:
        params['state'] = state
    if connect_calendar:
        params['scope'] = scopes_connection
        params['redirect_uri'] = redirect_uri_connection
    else:
        params['scope'] = scopes_login
        params['redirect_uri'] = redirect_uri
    return f'https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}'


def request_exchange_code(code: str, connect_calendar=False):
    params = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code'
    }
    if connect_calendar:
        params['redirect_uri'] = redirect_uri_connection
    else:
        params['redirect_uri'] = redirect_uri
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post('https://oauth2.googleapis.com/token', headers=headers, data=params)
    return json.loads(res.text)


def request_user_info(account: Account):
    res = create_authorized_request(url=Constants.GOOGLE_OAUTH2_API_URL + 'userinfo/v2/me',
                                    account=account, method=Constants.GET_METHOD)
    return res


def convert_to_calendar(response: dict):
    calendar = Calendar()
    calendar.platform_id = response.get('id')
    calendar.type = Constants.ACCOUNT_TYPE_GOOGLE
    calendar.description = response.get('description')
    calendar.location = response.get('location')
    calendar.summary = response.get('summary')
    calendar.timezone = response.get('timeZone')
    calendar.background_color = response.get('backgroundColor')
    calendar.color_id = response.get('colorId')
    calendar.default_reminders = response.get('defaultReminders')
    calendar.foreground_color = response.get('foregroundColor')
    calendar.notification_settings = response.get('notificationSettings')
    return calendar


# def full_synchronous_calendars(connection: Connection):
#     result = []
#     sync_token = connection.sync_token
#     if sync_token:
#         page_token, events = None, []
#         try:
#             while True:
#                 params = {
#                     'maxResult': Constants.GOOGLE_MAX_RESULT_RESPONSE,
#                     'pageToken': page_token,
#                     'syncToken': sync_token
#                 }
#                 res = create_authorized_request(url=Constants.GOOGLE_CALENDAR_API_URL + 'calendarList/list',
#                                                 account=connection,
#                                                 method=Constants.GET_METHOD,
#                                                 params=params)
#                 sync_calendars_by_linked_account(connection, res.get('items'))
#                 page_token = res.get('nextPageToken')
#                 if not page_token:
#                     connection.next_sync_token = res.get('nextSyncToken')
#                     break
#         except Exception:
#             # A 410 status code, "Gone", indicates that the sync token is invalid.
#             load_association_calendars_by_linked_account(connection)
#     else:
#         load_association_calendars_by_linked_account(connection)
#
#
# def sync_calendars_by_linked_account(connection: Connection, items: List[dict]):
#     db_calendars_supplier = [item.calendar.platform_id for item in connection.association_calendars]
#     db_calendars = [item.calendar for item in connection.association_calendars]
#     supplier_id_calendars_map = dict(zip(db_calendars_supplier, db_calendars))
#     supplier_id_association_calendars_map = dict(zip(db_calendars_supplier, connection.association_calendars))
#     for item in items:
#         calendar_response = convert_to_calendar(item)
#         if calendar_response.supplier_id in supplier_id_calendars_map:
#             if item.get('deleted'):
#                 supplier_id_association_calendars_map[calendar_response.supplier_id].access_role = \
#                     Constants.ACCESS_ROLE_DELETED
#                 pass
#             else:
#                 supplier_id_calendars_map[calendar_response.supplier_id].calendar.update(calendar_response,,
#         else:
#             association_calendar = ConnectionCalendar()
#             association_calendar.access_role = item.get('accessRole')
#             association_calendar.calendar = calendar_response
#             association_calendar.linked_account = connection
#             connection.association_calendars.append(association_calendar)


def load_association_calendars_by_linked_account(connection: Connection) -> List[ConnectionCalendar]:
    result: List[ConnectionCalendar] = []
    page_token = None
    while True:
        params = {
            'maxResult': Constants.GOOGLE_MAX_RESULT_RESPONSE,
            'pageToken': page_token
        }
        res = create_authorized_request(url=Constants.GOOGLE_CALENDAR_API_URL + 'users/me/calendarList',
                                        account=connection,
                                        method=Constants.GET_METHOD,
                                        params=params)

        for item_calendar in res.get('items'):
            calendar = convert_to_calendar(item_calendar)
            connection_calendar = ConnectionCalendar()
            connection_calendar.default_flag = True if item_calendar.get('primary') else False
            access_role = item_calendar.get('accessRole')
            match access_role:
                case 'owner':
                    connection_calendar.owner_flag = True
                    connection_calendar.access_role = Constants.ACCESS_ROLE_READ + Constants.ACCESS_ROLE_WRITE + Constants.ACCESS_ROLE_SHARE
                case 'writer':
                    connection_calendar.access_role = Constants.ACCESS_ROLE_WRITE + Constants.ACCESS_ROLE_WRITE
                case 'reader':
                    connection_calendar.access_role = Constants.ACCESS_ROLE_READ
                case _:
                    connection_calendar.owner_flag = False

            connection_calendar.linked_account = connection
            connection_calendar.calendar = calendar

            result.append(connection_calendar)
        page_token = res.get('nextPageToken')
        if not page_token:
            connection.sync_token = res.get('nextSyncToken')
            return result


def load_association_events_by_calendar(calendar: Calendar, connection: Connection) -> List[CalendarEvent]:
    page_token = None
    result = []
    while True:
        params = {
            'maxResult': Constants.GOOGLE_MAX_RESULT_RESPONSE,
            'pageToken': page_token
        }
        calendar_id = urllib.parse.quote(calendar.platform_id)
        response = create_authorized_request(
            url=Constants.GOOGLE_CALENDAR_API_URL + f'calendars/{calendar_id}/events',
            account=connection,
            method=Constants.GET_METHOD,
            params=params
        )

        for item in response.get('items'):
            event = convert_to_event(item, calendar)
            association_event = CalendarEvent()
            association_event.event = event
            association_event.owner_flag = True if item.get('creator') and item.get('creator').get('self') else False
            result.append(association_event)
        page_token = response.get('nextPageToken')
        if not page_token:
            calendar.next_sync_token = response.get('nextSyncToken')
            return result


def convert_to_event(response: dict, calendar: Calendar) -> Event:
    event = Event()
    event.calendar_id = calendar.id
    event.platform_id = response.get('id')
    event.attachments = response.get('attachments')
    event.description = response.get('description')
    event.color_id = response.get('colorId')
    event.conference_data = response.get('conferenceData')
    event.creator = response.get('creator')
    event.end = response.get('end')
    event.end_time_unspecified = response.get('endTimeUnspecified')
    event.event_type = response.get('eventType')
    event.extended_properties = response.get('extendedProperties')
    event.guests_can_invite_others = response.get('guestsCanInviteOthers')
    event.guests_can_modify = response.get('guestsCanModify')
    event.guests_can_see_other_guests = response.get('guestsCanSeeOtherGuests')
    event.html_link = response.get('htmlLink')
    event.uid = response.get('iCalUID')
    event.location = response.get('location')
    event.locked = response.get('locked')
    event.organizer = response.get('organizer')
    event.original_start_time = response.get('originalStartTime')
    event.private_copy = response.get('privateCopy')
    event.recurrence = response.get('recurrence')
    event.recurring_event_id = response.get('recurring_event_id')
    event.reminders = response.get('reminders')
    event.start = response.get('start')
    event.status = response.get('status')
    event.summary = response.get('summary')
    event.transparent = response.get('transparency')
    event.updated = response.get('updated')
    event.visibility = response.get('visibility')
    return event


def create_connection(credentials: dict) -> Connection:
    result = Connection()
    result.credentials = credentials
    payload = jwt.decode(credentials.get('id_token'), options={"verify_signature": False})
    result.email = result.username = payload.get('email')
    result.platform_id = payload.get('sub')
    result.type = Constants.ACCOUNT_TYPE_GOOGLE
    result.created_at = result.updated_at = datetime.datetime.utcnow()
    return result


def representation_calendar(calendar) -> dict:
    result = {
        'summary': calendar.summary,
        'description': calendar.description,
        'location': calendar.location,
        'timeZone': calendar.timezone
    }

    return dict_utils.remove_empty_or_none(result)


def create_calendar(calendar: Calendar, connection: Connection) -> Calendar:
    res = create_authorized_request(url=Constants.GOOGLE_CREATE_CALENDAR_API_URL,
                                    account=connection,
                                    method=Constants.POST_METHOD,
                                    json=representation_calendar(calendar=calendar))

    return convert_to_calendar(res)


def update_calendar(calendar: Calendar, connection: Connection) -> Calendar:
    res = create_authorized_request(
        url=Constants.GOOGLE_UPDATE_PATCH_DELETE_CALENDAR_API_URL.format(calendar_id=calendar.platform_id),
        account=connection,
        method=Constants.PUT_METHOD,
        json=representation_calendar(calendar=calendar)
    )
    return convert_to_calendar(res)


def delete_calendar(calendar: Calendar, connection: Connection) -> None:
    create_authorized_request(
        url=Constants.GOOGLE_UPDATE_PATCH_DELETE_CALENDAR_API_URL.format(calendar_id=calendar.platform_id),
        account=connection,
        method=Constants.DELETE_METHOD
    )


def patch_calendar(calendar: Calendar, data: Calendar, connection: Connection) -> Calendar:
    res = create_authorized_request(
        url=Constants.GOOGLE_UPDATE_PATCH_DELETE_CALENDAR_API_URL.format(calendar_id=calendar.platform_id),
        account=connection,
        method=Constants.PATCH_METHOD,
        json=representation_calendar(calendar=data)
    )
    return convert_to_calendar(res)
