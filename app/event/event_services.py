import datetime
from typing import List

from sqlalchemy.orm import Session

from app.association import CalendarEvent, association_dao
from app.calendar import calendar_dao
from app.calendar.calendar import Calendar
from app.connection import connection_dao
from app.connection.connection import Connection
from app.constants import Constants
from app.event import event_dao
from app.event.event import Event
from app.schemas import event_schema
from app.utils import platform_utils, validate_utils


def load_events_by_calendar(calendar: Calendar, connection: Connection, session: Session) -> List[CalendarEvent]:
    association_events = platform_utils.get(connection).load_association_events_by_calendar(calendar, connection)

    # check whether existing event in db or not
    event_platform_ids = [item.event.platform_id for item in association_events]
    # platform_id_association_map = dict(zip(event_platform_ids, association_events))

    db_events = event_dao.find_by_list_platform_id_and_type(platform_ids=event_platform_ids,
                                                            platform_type=calendar.type,
                                                            session=session)

    db_event_platform_ids = [item.platform_id for item in db_events]
    platform_id_db_event_map = dict(zip(db_event_platform_ids, db_events))

    for item in association_events:
        if item.event.platform_id in platform_id_db_event_map:
            item.calendar_id = calendar.id
            item.calendar = None
            item.event_id = platform_id_db_event_map[item.event.platform_id].id
            item.event = None
            session.add(item)
            association_events.remove(item)

    return association_events


def validate_get_by_id(sub, event_id, session):
    return None


def find_by_id(event_id: int, session: Session):
    return event_dao.find_by_id(event_id=event_id, session=session)


def validate_create_event(sub: int, data: dict, session: Session):
    required_fields = 'calendar_id', 'end', 'start'
    validate_utils.validate_required_field(data, *required_fields)
    if data.get('connection_id') and not connection_dao.is_connected(sub, data.get('connection_id'), session):
        raise PermissionError(
            'Not found connection between sub and connection: {}, {}'.format(sub, data.get('connection_id')))
    if not calendar_dao.can_edit(sub, calendar_id=data.get('calendar_id'), session=session):
        raise PermissionError('Don\'t allowed to edit calendar with id={}'.format(data.get('calendar_id')))
    validate_utils.start_end_time(data.get('start'), data.get('end'), time_format=Constants.EVENT_TIME_FORMAT)


def create_event(sub: int, data: dict, session: Session) -> Event:
    if 'connection_id' in data:
        connection = connection_dao.find_by_id(data.get('connection_id'), session)
    else:
        connection = connection_dao.get_connection_can_edit(sub=sub, calendar_id=data.get('calendar_id'),
                                                            session=session)
    calendar = calendar_dao.find_by_id(data.get('calendar_id'), session)
    event = event_schema.load(data)
    response_event = platform_utils.get(connection).create_event(event, calendar, connection)

    return response_event


def validate_update(sub, event, data, session):
    if not event_dao.can_edit(sub=sub, event_id=event.id, session=session):
        raise PermissionError('Don\'t allowed to edit event with id = {} '.format(event.id))
    start, end = data.get('start', event.start), data.get('end', event.end)
    validate_utils.start_end_time(start=start, end=end, time_format=Constants.EVENT_TIME_FORMAT)


def update_event(sub, event, data, session):
    event.updated(event_schema.load(data))
    return None
