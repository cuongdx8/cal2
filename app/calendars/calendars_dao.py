from typing import List

from sqlalchemy.orm import Session

from app.calendars.calendars import Calendar
from app.constants import Constants


def find_by_id(calendar_id: int, session: Session) -> Calendar:
    return session.query(Calendar).filter(Calendar.id == calendar_id).first()


def find_by_connection_id(connection_id: int, session: Session) -> List[Calendar]:
    sql = 'select cal.* from calendars cal ' \
          'join connection_calendar cc ' \
          'on cal.id = cc.calendar_id ' \
          f'where cc.connection_id = {connection_id}'
    rs = session.execute(sql).all()
    result = []
    for item in rs:
        item_dict = dict(zip(item.keys(), item))
        result.append(Calendar(**item_dict))
    return result


def find_by_account_id(sub: int, session: Session) -> List[Calendar]:
    sql = 'select * from calendars ' \
          'where id in (' \
          'select cc.calendar_id from connection_calendar cc ' \
          'join connections con ' \
          'on cc.connection_id = con.id ' \
          'join account_connection ac ' \
          'on con.id = ac.connection_id ' \
          f'where ac.account_id = {sub})'
    rs = session.execute(sql).all()
    result = []
    for item in rs:
        item_dict = dict(zip(item.keys(), item))
        result.append(Calendar(**item_dict))
    return result


def find_by_list_platform_id_and_type(platform_id: List[str], calendar_type: str, session: Session) -> List[Calendar]:
    # sql = f'select id, platform_id from calendars where platform_id in {set(platform_id)} and type = {calendar_type}'
    return session.query(Calendar).filter(Calendar.platform_id.in_(platform_id), Calendar.type == calendar_type).all()


def find_by_platform_id_and_type(platform_id: str, calendar_type: str, session: Session):
    return session.query(Calendar).filter(Calendar.platform_id == platform_id, Calendar.type == calendar_type).first()


def is_owner(sub: int, calendar_id: int, session: Session) -> bool:
    sql = f'select count(1) from account_connection ' \
          f'join connection_calendar ' \
          f'on account_connection.connection_id = connection_calendar.connection_id ' \
          f'where account_connection.account_id = {sub} and connection_calendar.calendar_id = {calendar_id} ' \
          f'and connection_calendar.owner_flag'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def can_read(sub: int, calendar_id: int, session: Session) -> bool:
    sql = f'select count(1) from account_connection ' \
          f'join connection_calendar ' \
          f'on account_connection.connection_id = connection_calendar.connection_id ' \
          f'where account_connection.account_id = {sub} and connection_calendar.calendar_id = {calendar_id}'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def can_edit(sub: int, calendar_id: int, session: Session) -> bool:
    sql = f'select count(1) from account_connection ' \
          f'join connection_calendar ' \
          f'on account_connection.connection_id = connection_calendar.connection_id ' \
          f'where account_connection.account_id = {sub} and connection_calendar.calendar_id = {calendar_id} ' \
          f"and connection_calendar.access_role like '%{Constants.ACCESS_ROLE_WRITE}%'"
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def add(calendar: Calendar, session: Session) -> None:
    session.add(calendar)


def delete_by_connection_ids(calendar_id: int, connection_ids: List[int], session: Session):
    session.execute(f'call delete_calendar_by_connection_ids({calendar_id}, ARRAY[{connection_ids}])')


def merge(calendar: Calendar, session: Session):
    session.merge(calendar)


def is_default(calendar_id: int, session: Session):
    sql = f'select count(1) from connection_calendar where calendar_id = {calendar_id} and default_flag'
    result = session.execute(sql).scalar()
    return True if result > 0 else False
