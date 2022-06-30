import datetime

from sqlalchemy.orm import Session

from app.connection.connection import Connection


def add(connection: Connection, session: Session):
    connection.updated_at = datetime.datetime.utcnow()
    if connection.id:
        session.merge(connection)
    else:
        connection.created_at = connection.updated_at
        session.add(connection)


def find_by_id(connection_id: str, session: Session):
    connection = session.query(Connection).filter(Connection.id == connection_id).first()
    return connection


def find_by_platform_id_and_type(platform_id: str, connection_type: str, session: Session) -> Connection:
    return session.query(Connection).filter(Connection.platform_id == platform_id, Connection.type == connection_type)\
        .first()


def is_owner(sub: str, connection_id: str, session: Session):
    sql = f'select count(1) from account_connection where account_id = {sub} and connection_id = {connection_id}'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def delete(connection: Connection, session: Session):
    session.delete(connection)


def is_existing(connection: Connection, session: Session):
    sql = f'select count(1) from connection where platform_id = \'{connection.platform_id}\' and type = \'{connection.type}\''
    count = session.execute(sql).scalar()
    return True if count > 0 else False


def disconnect(sub, connection_id, session):
    session.execute(f'call disconnect_connection({connection_id}, {sub})')