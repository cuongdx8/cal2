from typing import List

from sqlalchemy.orm import Session

from app.calendar.calendar import Calendar
from app.constants import Constants


def find_by_id(calendar_id: int, session: Session) -> Calendar:
    return session.query(Calendar).filter(Calendar.id == calendar_id).first()


def find_by_list_platform_id_and_type(platform_id: List[str], calendar_type: str, session: Session) -> List[Calendar]:
    # sql = f'select id, platform_id from calendar where platform_id in {set(platform_id)} and type = {calendar_type}'
    return session.query(Calendar).filter(Calendar.platform_id.in_(platform_id), Calendar.type == calendar_type).all()


def find_by_platform_id_and_type(platform_id: str, calendar_type: str, session: Session):
    return session.query(Calendar).filter(Calendar.platform_id == platform_id, Calendar.type == calendar_type).first()


def is_owner(sub: int, calendar_id: int, session: Session) -> bool:
    sql = f'select count(1) from account_connection ' \
          f'join connection_calendar ' \
          f'on account_connection.connection_id = connection_calendar.connection_id ' \
          f'where account_connection.account_id = {sub} and calendar_connection.calendar_id = {calendar_id} ' \
          f'and connection_calendar.access_role = {Constants.ACCESS_ROLE_OWNER}'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def can_read(sub: int, calendar_id: int, session: Session) -> bool:
    sql = f'select count(1) from account_connection ' \
          f'join connection_calendar ' \
          f'on account_connection.connection_id = connection_calendar.connection_id ' \
          f'where account_connection.account_id = {sub} and connection_calendar.calendar_id = {calendar_id}'
    result = session.execute(sql).scalar()
    return True if result > 0 else False


def add(calendar: Calendar, session: Session) -> None:
    session.add(calendar)
