import datetime
from typing import List

from sqlalchemy.orm import Session

from app.connection.connection import Connection
from app.constants import Constants


def add(connection: Connection, session: Session):
    connection.updated_at = datetime.datetime.utcnow()
    if connection.id:
        session.merge(connection)
    else:
        connection.created_at = connection.updated_at
        session.add(connection)


def find_by_id(connection_id: int, session: Session):
    connection = session.query(Connection).filter(Connection.id == connection_id).first()
    return connection


def find_by_platform_id_and_type(platform_id: str, connection_type: str, session: Session) -> Connection:
    return session.query(Connection).filter(Connection.platform_id == platform_id, Connection.type == connection_type)\
        .first()


def is_owner(sub: int, connection_id: int, session: Session):
    sql = f'select count(1) from account_connection where account_id = {sub} and connection_id = {connection_id}'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def delete(connection: Connection, session: Session) -> None:
    session.delete(connection)


def is_existing(connection: Connection, session: Session) -> bool:
    sql = f'select count(1) from connection where platform_id = \'{connection.platform_id}\' and type = \'{connection.type}\''
    count = session.execute(sql).scalar()
    return True if count > 0 else False


def disconnect(sub: int, connection_id: int, session: Session) -> None:
    session.execute(f'call disconnect_connection({connection_id}, {sub})')


def get_connection_can_edit(sub: int, calendar_id: int, session: Session) -> Connection:
    sql = 'select c.* from connection c join account_connection ac ' \
          'on ac.connection_id = c.id ' \
          'join connection_calendar cc ' \
          'on c.id = cc.connection_id ' \
          f"where ac.account_id = {sub} and cc.calendar_id = {calendar_id} and cc.access_role like '%{Constants.ACCESS_ROLE_WRITE}%' "
    res = session.execute(sql).fetchone()
    res_dict = dict(zip(res.keys(), res))
    return Connection(**res_dict)


def between_sub_and_calendar(sub: int, calendar_id: int, session: Session) -> List[Connection]:
    sql = 'select c.* from connection c join account_connection ac ' \
          'on ac.connection_id = c.id ' \
          'join connection_calendar cc ' \
          'on c.id = cc.connection_id ' \
          f'where ac.account_id = {sub} and cc.calendar_id = {calendar_id}'
    res = session.execute(sql).all()
    result = []
    for item in res:
        res_dict = dict(zip(item.keys(), item))
        result.append(Connection(**res_dict))
    return result
