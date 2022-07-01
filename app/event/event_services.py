from typing import List

from sqlalchemy.orm import Session

from app.association import CalendarEvent
from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.constants import Constants
from app.event import event_dao
from app.utils import gg_utils, mic_utils


def load_events_by_calendar(calendar: Calendar, connection: Connection, session: Session) -> List[CalendarEvent]:
    match connection.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            platform_utils = gg_utils
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            platform_utils = mic_utils
        case _:
            raise ValueError('Connection type is invalid')
    association_events = platform_utils.load_association_events_by_calendar(calendar, connection)

    # check whether existing event in db or not
    event_platform_ids = [item.event.platform_id for item in association_events]
    platform_id_association_map = dict(zip(event_platform_ids, association_events))

    db_events = event_dao.find_by_list_platform_id_and_type(platform_ids=event_platform_ids,
                                                            event_type=Constants.ACCOUNT_TYPE_GOOGLE,
                                                            session=session)
    for item in db_events:
        if item.platform_id in platform_id_association_map:
            platform_id_association_map[item.platform_id].event = item
            platform_id_association_map[item.platform_id].event_id = item.id

    return association_events
