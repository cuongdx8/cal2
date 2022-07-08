import datetime
from typing import List

from sqlalchemy.orm import Session

from app.association import CalendarEvent, ConnectionCalendar, association_dao
from app.calendar import calendar_dao
from app.calendar.calendar import Calendar
from app.connection import connection_dao, connection_services
from app.connection.connection import Connection
from app.constants import Constants
from app.schemas import calendar_schema
from app.utils import platform_utils, validate_utils


def find_by_id(calendar_id: int, session: Session) -> Calendar:
    return calendar_dao.find_by_id(calendar_id=calendar_id, session=session)


def get_association_calendar_by_connection(connection: Connection, session: Session) -> List[CalendarEvent]:
    association_calendars = platform_utils.get(connection).load_association_calendars_by_linked_account(connection)
    calendar_platform_ids = [item.calendar.platform_id for item in association_calendars]
    db_calendars = calendar_dao.find_by_list_platform_id_and_type(calendar_platform_ids,
                                                                  calendar_type=Constants.ACCOUNT_TYPE_GOOGLE,
                                                                  session=session)
    db_calendar_platform_id = [item.platform_id for item in db_calendars]
    platform_id_db_association_map = dict(zip(db_calendar_platform_id, db_calendars))

    for item in association_calendars:
        if item.calendar.platform_id in platform_id_db_association_map:
            item.calendar_id = platform_id_db_association_map[item.calendar.platform_id].id
            item.calendar = None
            item.connection_id = connection.id
            item.connection = None
            session.add(item)
            association_calendars.remove(item)
    return association_calendars


def can_read(sub: int, calendar_id: int, session: Session) -> bool:
    return calendar_dao.can_read(sub, calendar_id, session)


def validate_create(sub: int, data: dict, session: Session):
    validate_utils.validate_required_field(data, 'connection_id', 'summary')
    if not connection_dao.is_connected(sub=sub, connection_id=data.get('connection_id'), session=session):
        raise PermissionError(
            f'Not permission to create calendar on on connection with id = {data.get("connection_id")}'
        )
    validate_utils.validate_timezone(data.get('timezone'))


def init_calendar(connection: Connection, data: dict) -> Calendar:
    calendar = calendar_schema.load(data)
    calendar.created_by = {
        'email': connection.email,
        'name': connection.username
    }
    calendar.created_at = calendar.updated_at = datetime.datetime.utcnow()
    calendar.type = connection.type
    return calendar


def create(data, session):
    connection = connection_dao.find_by_id(data.get('connection_id'), session)
    calendar = init_calendar(connection, data)
    calendar = platform_utils.get(calendar).create_calendar(calendar, connection)

    # create association
    association = ConnectionCalendar()
    association.calendar = calendar
    association.connection = connection
    association.access_role = Constants.ACCESS_ROLE_READ + Constants.ACCESS_ROLE_WRITE + Constants.ACCESS_ROLE_SHARE
    association.owner_flag = True
    association.default_flag = False

    calendar_dao.add(calendar, session)
    # TODO channel_notification_services.create_by_calendar(calendar, linked_account, session)
    calendar.association_connections = [association]

    return calendar


def validate_delete(sub, calendar_id, connection_id, session):
    if calendar_dao.is_default(calendar_id, session):
        raise PermissionError('Cannot remove default calendar.')


def delete(sub: int, calendar_id: int, connection_id: str, session: Session):
    calendar = calendar_dao.find_by_id(calendar_id, session)
    if connection_id:
        connection = connection_dao.find_by_id(connection_id=int(connection_id), session=session)
    else:
        connection = connection_dao.between_sub_and_calendar(sub=sub, calendar_id=calendar_id, session=session)
        if len(connection) == 0:
            raise PermissionError('Cannot remove calendar with id = {}'.format(calendar_id))

    for item in connection:
        platform_utils.get(item).delete_calendar(calendar, item)
    calendar_dao.delete_by_connection_ids(calendar_id=calendar_id, connection_ids=[item.id for item in connection], session=session)
    return None


def validate_patch(sub: int, calendar_id: int, data: dict, session: Session):
    validate_utils.must_not_contain_fields(data, 'id', 'platform_id', 'created_by')
    if not calendar_dao.can_edit(sub=sub, calendar_id=calendar_id, session=session):
        raise PermissionError(
            f'Not permission to create calendar on on connection with id = {data.get("connection_id")}'
        )
    if data.get('timezone'):
        validate_utils.validate_timezone(data.get('timezone'))
    # if data.get('summary'):
    #     validate_utils.validate_can_only_contain_alpha_character('summary', data.get('summary'))
    # if data.get('description'):
    #     validate_utils.validate_can_only_contain_alpha_character('description', data.get('description'))


def patch(sub, calendar_id, data, session):
    calendar = calendar_dao.find_by_id(calendar_id, session)
    connection = connection_dao.get_connection_can_edit(sub=sub, calendar_id=calendar_id, session=session)
    res_calendar = platform_utils.get(calendar).patch_calendar(calendar, calendar_schema.load(data), connection)
    calendar.update(res_calendar)
    calendar_dao.merge(calendar, session)
    return calendar


def validate_find_by_connection_id(sub: int, connection_id: int, session: Session):
    if not connection_services.is_connected(sub=sub, connection_id=connection_id, session=session):
        raise PermissionError('Not found connect between sub and connection_id, {sub} {connection_id}'.format(sub=sub, connection_id=connection_id))


def find_by_connection_id(connection_id: int, session: Session) -> List[Calendar]:
    return calendar_dao.find_by_connection_id(connection_id=connection_id, session=session)


def find_by_account_id(sub: int, session: Session) -> List[Calendar]:
    return calendar_dao.find_by_account_id(sub=sub, session=session)
