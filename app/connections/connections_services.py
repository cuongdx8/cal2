from sqlalchemy.orm import Session

from app.users import users_dao
from app.calendars import calendars_services
from app.connections import connections_dao
from app.connections.connections import Connection
from app.events import events_services
from app.exception import DuplicateConnection
from app.utils import platform_utils


def connect(sub: int, connection: Connection, session: Session):
    account = users_dao.find_by_id(sub, session)
    connection = platform_utils.get(connection).create_connection(credentials=connection.credentials)
    if connections_dao.is_existing(connection=connection, session=session):
        # connections is existing in db
        connection = connections_dao.find_by_platform_id_and_type(connection.platform_id, connection.type,
                                                                  session)
        if connection in account.connections:
            raise DuplicateConnection
    else:
        connections_dao.add(connection, session)
        session.flush()
        # connections is not exists in db
        association_calendars = calendar_services.get_association_calendar_by_connection(connection, session)
        connection.association_calendars = association_calendars
        session.flush()
        for item in association_calendars:
            if item.calendar.id:
                item.calendar.association_events = events_services.load_events_by_calendar(item.calendar, connection,
                                                                                           session)
    account.connections.append(connection)


def validate_disconnect(sub: int, connection_id: int, session: Session) -> None:
    if not connections_dao.is_connected(sub=sub, connection_id=connection_id, session=session):
        raise PermissionError


def disconnect(sub: int, connection_id: int, session: Session) -> None:
    connections_dao.disconnect(sub, connection_id, session)


def is_connected(sub: int, connection_id: int, session: Session):
    return connections_dao.is_connected(sub=sub, connection_id=connection_id, session=session)
