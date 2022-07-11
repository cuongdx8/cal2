from sqlalchemy.orm import Session

from app.bookings.bookings import Booking


def find_by_account_id(sub: int, session: Session):
    return session.query(Booking).filter(Booking.account_id == sub).all()


def find_by_id(booking_id, session):
    return session.query(Booking).filter(Booking.id == booking_id).first()


def add(booking: int, session: Session):
    session.add(booking)


def update(booking: Booking, session: Session):
    session.merge(booking)


def delete(booking: Booking, session: Session):
    session.delete(booking)