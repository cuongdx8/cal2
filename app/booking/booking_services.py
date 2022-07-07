from typing import List

from sqlalchemy.orm import Session

from app.booking import booking_dao
from app.booking.booking import Booking
from app.schemas import booking_schema


def me(sub: int, session: Session) -> List[Booking]:
    return booking_dao.find_by_account_id(sub=sub, session=session)


def find_by_id(booking_id: int, session: Session) -> Booking:
    return booking_dao.find_by_id(booking_id, session)


def validate_create(data, session):
    return None


def create(sub, data, session):
    booking = booking_schema.load(data)
    booking.account_id = sub
    booking_dao.add(booking, session)
    return booking


def validate_update(sub, booking_id, data, session):
    booking = find_by_id(booking_id, session=session)
    if booking.account_id != int(sub):
        raise PermissionError('You don\'t have any booking with id=: {}'.format(booking_id))
    # TODO validate
    return booking


def update(booking: Booking, data: dict, session: Session):
    booking.update(booking_schema.load(data))
    booking_dao.update(booking, session)
    return booking


def delete(booking, session):
    booking_dao.delete(booking, session)