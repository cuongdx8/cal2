import datetime

import jwt
from sqlalchemy.orm import Session

from app.account import account_dao
from app.calendar import calendar_services
from app.connection.connection import Connection
from app.constants import Constants
from app.event import event_services


def connect(sub: str, connection: Connection, session: Session):
    account = account_dao.find_by_id(sub, session)
    match connection.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            connection = create_connection(connection_type=connection.type, credentials=connection.credentials)
            association_calendars = calendar_services.get_association_calendar_by_connection(connection, session)
            for item in association_calendars:
                item.calendar.events = event_services.load_events_by_calendar(item.calendar, connection)
            connection.association_calendars = association_calendars
        case _:
            raise ValueError('connection\'s type is invalid')
    account.connections.append(connection)


def create_connection(connection_type: str, credentials: dict):
    result = Connection()
    result.credentials = credentials
    match connection_type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            payload = jwt.decode(credentials.get('id_token'), options={"verify_signature": False})
            result.email = result.username = payload.get('email')
            result.platform_id = payload.get('sub')
            result.type = Constants.ACCOUNT_TYPE_GOOGLE
            result.created_at = result.updated_at = datetime.datetime.utcnow()
        case _:
            raise ValueError('connection\'s type is invalid')
    return result
