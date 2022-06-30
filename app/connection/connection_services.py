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
from app.utils import mic_utils


def connect(sub: str, connection: Connection, session: Session):
    account = account_dao.find_by_id(sub, session)
    connection = create_connection(connection_type=connection.type, credentials=connection.credentials)
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
            if not item.calendar.id:
                item.calendar.events = event_services.load_events_by_calendar(item.calendar, connection)
        connection.association_calendars = association_calendars

    account.connections.append(connection)


def create_connection(connection_type: str, credentials: dict) -> Connection:
    result = Connection()
    result.credentials = credentials
    match connection_type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            payload = jwt.decode(credentials.get('id_token'), options={"verify_signature": False})
            result.email = result.username = payload.get('email')
            result.platform_id = payload.get('sub')
            result.type = Constants.ACCOUNT_TYPE_GOOGLE
            result.created_at = result.updated_at = datetime.datetime.utcnow()
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            payload = mic_utils.get_profile(credentials=credentials)
            result.type = Constants.ACCOUNT_TYPE_MICROSOFT
            result.platform_id = payload.get('id')
            result.username = f'{payload.get("givenName")} {payload.get("surname")}'
            result.email = payload.get('userPrincipalName')
        case _:
            raise ValueError('connection\'s type is invalid')
    return result


def validate_disconnect(sub: str, connection_id: str, session: Session) -> None:
    if not connection_dao.is_owner(sub=sub, connection_id=connection_id, session=session):
        raise PermissionError


def disconnect(sub: str, connection_id: str, session: Session) -> None:
    connection_dao.disconnect(sub, connection_id, session)