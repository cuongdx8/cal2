from typing import List

from sqlalchemy.orm import Session

from app.association import CalendarEvent
from app.calendar.calendar import Calendar
from app.connection import connection_dao
from app.connection.connection import Connection
from app.constants import Constants
from app.event import event_dao
from app.event.event import Event
from app.utils import platform_utils, validate_utils


def load_events_by_calendar(calendar: Calendar, connection: Connection, session: Session) -> List[CalendarEvent]:
    association_events = platform_utils.get(connection).load_association_events_by_calendar(calendar, connection)

    # check whether existing event in db or not
    event_platform_ids = [item.event.platform_id for item in association_events]
    # platform_id_association_map = dict(zip(event_platform_ids, association_events))

    db_events = event_dao.find_by_list_platform_id_and_type(platform_ids=event_platform_ids,
                                                            event_type=calendar.type,
                                                            session=session)

    db_event_platform_ids = [item.id for item in db_events]
    platform_id_db_event_map = dict(zip(db_event_platform_ids, db_events))

    for item in association_events:
        if item.event.platform_id in platform_id_db_event_map:
            item.event_id = platform_id_db_event_map[item.event.platform_id].id
            item.event = None
        item.calendar = calendar

    return association_events


def validate_get_by_id(sub, event_id, session):
    return None


def find_by_id(event_id: int, session: Session):
    return event_dao.find_by_id(event_id=event_id, session=session)


def validate_create_event(sub: int, data: dict, session: Session):
    required_fields = 'connection_id', 'end', 'start'
    validate_utils.validate_required_field(data, *required_fields)
    if not connection_dao.is_connected(sub, data.get('connection_id'), session):
        raise PermissionError('Not found connection between sub and connection: {}, {}'.format(sub, data.get('connection_id')))


def init_event(connection, data):
    pass


def create_event(data: dict, session: Session) -> Event:
    connection = connection_dao.find_by_id(data.get('connection_id'), session)
    event = init_event(connection, data)
    return None