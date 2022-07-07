from typing import List

from sqlalchemy.orm import Session

from app.booking.availability.availability import Availability


def find_by_account_id(sub: int, session: Session) -> List[Availability]:
    return session.query(Availability).filter(Availability.account_id == sub).all()


def find_by_id(availability_id: int, session: Session) -> Availability:
    return session.query(Availability).filter(Availability.id == availability_id).first()


def add(availability: Availability, session: Session):
    if availability.default_flag:
        session.execute('UPDATE availability set default_flag=false where default_flag=true')
    session.add(availability)


def set_default(availability_id: int, session: Session):
    session.execute('UPDATE availability SET default_flag=false WHERE default_flag=true')
    session.execute(f'UPDATE availability SET default_flag=true WHERE id={availability_id}')


def delete(availability: Availability, session: Session):
    session.delete(availability)


def update(availability: Availability, session: Session):
    session.merge(availability)
