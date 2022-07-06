from typing import List

from sqlalchemy.orm import Session

from app.event.event import Event


def find_by_list_platform_id_and_type(platform_ids: List[str], event_type: str, session: Session) -> List[Event]:
    return session.query(Event).filter(Event.platform_id.in_(platform_ids),
                                       Event.event_type == event_type).all()


def find_by_id(event_id: int, session: Session):
    return session.query(Event).filter(Event.id == event_id).first()
