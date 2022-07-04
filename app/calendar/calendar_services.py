from typing import List

from sqlalchemy.orm import Session

from app.association import CalendarEvent
from app.calendar import calendar_dao
from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.constants import Constants
from app.utils import gg_utils, mic_utils


def find_by_id(calendar_id: int, session: Session) -> Calendar:
    return calendar_dao.find_by_id(calendar_id=calendar_id, session=session)


def get_association_calendar_by_connection(connection: Connection, session: Session) -> List[CalendarEvent]:
    match connection.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            platform_utils = gg_utils
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            platform_utils = mic_utils
        case _:
            raise ValueError('Connection\'s type is invalid')

    association_calendars = platform_utils.load_association_calendars_by_linked_account(connection)
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
        item.connection = connection

    return association_calendars


def can_read(sub: int, calendar_id: int, session: Session) -> bool:
    return calendar_dao.can_read(sub, calendar_id, session)


def validate_create(sub: int, data: dict, session: Session) -> bool:
    # TODO validate create calendar
    return True


def init_calendar(data: dict) -> Calendar:
    return Calendar()


def create(sub, data, session):
    calendar = init_calendar(data)
    connection = Connection()
    match calendar.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            platform_utils = gg_utils
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            platform_utils = mic_utils
        case _:
            raise ValueError('Calendar\'s type is invalid')
    platform_utils.create_calendar(calendar, connection)
    calendar_dao.add(calendar, session)
    # TODO channel_notification_services.create_by_calendar(calendar, linked_account, session)
