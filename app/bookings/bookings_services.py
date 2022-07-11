from typing import List

from sqlalchemy.orm import Session

from app.bookings import bookings_dao
from app.bookings.bookings import Booking
from app.schemas import bookings_schema


def me(sub: int, session: Session) -> List[Booking]:
    return bookings_dao.find_by_account_id(sub=sub, session=session)


def find_by_id(booking_id: int, session: Session) -> Booking:
    return bookings_dao.find_by_id(booking_id, session)


def validate_create(data, session):
    return None


def create(sub, data, session):
    booking = bookings_schema.load(data)
    booking.account_id = sub
    bookings_dao.add(booking, session)
    return booking


def validate_update(sub, booking_id, data, session):
    booking = find_by_id(booking_id, session=session)
    if booking.account_id != int(sub):
        raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
    # TODO validate
    return booking


def update(booking: Booking, data: dict, session: Session):
    booking.update(bookings_schema.load(data))
    bookings_dao.update(booking, session)
    return booking


def delete(booking, session):
    bookings_dao.delete(booking, session)