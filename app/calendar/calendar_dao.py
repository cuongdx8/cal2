from typing import List

from sqlalchemy.orm import Session

from app.calendar.calendar import Calendar


def find_by_list_platform_id_and_type(platform_id: List[str], calendar_type: str, session: Session):
    # sql = f'select id, platform_id from calendar where platform_id in {set(platform_id)} and type = {calendar_type}'
    return session.query(Calendar).filter(Calendar.platform_id.in_(platform_id), Calendar.type == calendar_type).all()
