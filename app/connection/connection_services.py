import datetime

import jwt
from sqlalchemy.orm import Session

from app.account import account_dao
from app.calendar import calendar_services
from app.connection import connection_dao
from app.connection.connection import Connection
from app.constants import Constants
from app.event import event_services
from app.exception import DuplicateConnection
from app.utils import mic_utils, gg_utils


def connect(sub: str, connection: Connection, session: Session):
    match connection.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            platform_utils = gg_utils
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            platform_utils = mic_utils
        case _:
            raise ValueError('connection type is invalid')
    account = account_dao.find_by_id(sub, session)
    connection = platform_utils.create_connection(credentials=connection.credentials)
    if connection_dao.is_existing(connection=connection, session=session):
        # connection is existing in db
        connection = connection_dao.find_by_platform_id_and_type(connection.platform_id, connection.type,
                                                                 session)
        if connection in account.connections:
            raise DuplicateConnection
    else:
        # connection is not exists in db
        association_calendars = calendar_services.get_association_calendar_by_connection(connection, session)
        for item in association_calendars:
            if item.calendar and not item.calendar.id:
                item.calendar.association_events = event_services.load_events_by_calendar(item.calendar, connection, session)

    account.connections.append(connection)


def validate_disconnect(sub: str, connection_id: str, session: Session) -> None:
    if not connection_dao.is_owner(sub=sub, connection_id=connection_id, session=session):
        raise PermissionError


def disconnect(sub: str, connection_id: str, session: Session) -> None:
    connection_dao.disconnect(sub, connection_id, session)
