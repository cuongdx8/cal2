from sqlalchemy.orm import Session

from app.calendar import calendar_dao
from app.connection.connection import Connection
from app.constants import Constants
from app.utils import gg_utils


def get_association_calendar_by_connection(connection: Connection, session: Session):
    match connection.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            association_calendar = gg_utils.load_association_calendars_by_linked_account(connection)
            calendar_platform_ids = [item.calendar.platform_id for item in association_calendar]
            platform_id_association_map = dict(zip(calendar_platform_ids, association_calendar))
            db_calendar = calendar_dao.find_by_list_platform_id_and_type(calendar_platform_ids,
                                                                         calendar_type=Constants.ACCOUNT_TYPE_GOOGLE,
                                                                         session=session)
            for item in db_calendar:
                if item.platform_id in platform_id_association_map:
                    platform_id_association_map[item.platform_id].calendar = item
                    platform_id_association_map[item.platform_id].calendar_id = item.id
            return association_calendar
        case _:
            ValueError('Connection\'s type is invalid')
