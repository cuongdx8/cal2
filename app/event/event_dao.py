from typing import List

from sqlalchemy.orm import Session

from app.event.event import Event


def find_by_list_platform_id_and_type(platform_ids: List[str], platform_type: str, session: Session) -> List[Event]:
    return session.query(Event).filter(Event.platform_id.in_(platform_ids),
                                       Event.type == platform_type).all()


def find_by_id(event_id: int, session: Session):
    return session.query(Event).filter(Event.id == event_id).first()


def can_edit(sub: int, event_id: int, session: Session):
    sql = f'select count(1) from account_connection ac' \
          f' where ac.account_id={sub} and ac.connection_id in (' \
          f'select cc.connection_id from connection_calendar cc ' \
          f'join calendar_event ce ' \
          f'on cc.calendar_id = ce.calendar_id ' \
          f'where ce.event_id = {event_id} )'
    rs = session.execute(sql).scalar
    return True if rs > 0 else False
