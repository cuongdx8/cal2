from sqlalchemy.orm import Session

from app.account import account_dao
from app.calendar import calendar_services
from app.connection import connection_dao
from app.connection.connection import Connection
from app.event import event_services
from app.exception import DuplicateConnection
from app.utils import platform_utils


def connect(sub: str, connection: Connection, session: Session):
    account = account_dao.find_by_id(sub, session)
    connection = platform_utils.get(connection).create_connection(credentials=connection.credentials)
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


def validate_disconnect(sub: int, connection_id: int, session: Session) -> None:
    if not connection_dao.is_connected(sub=sub, connection_id=connection_id, session=session):
        raise PermissionError


def disconnect(sub: int, connection_id: int, session: Session) -> None:
    connection_dao.disconnect(sub, connection_id, session)


def is_connected(sub: int, connection_id: int, session: Session):
    return connection_dao.is_connected(sub=sub, connection_id=connection_id, session=session)