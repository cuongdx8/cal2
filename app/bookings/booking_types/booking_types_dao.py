from sqlalchemy.orm import Session

from app.bookings.booking_types.booking_types import BookingType


def me(sub: int, session: Session):
    return session.query(BookingType).filter(BookingType.account_id == sub).all()


def find_by_id(booking_type_id: int, session: Session):
    return session.query(BookingType).filter(BookingType.id == booking_type_id).first()


def delete(booking_type: BookingType, session: Session):
    session.delete(booking_type)


def update(booking_type: BookingType, session: Session):
    return session.merge(booking_type)


def add(booking_type: BookingType, session: Session):
    return session.add(booking_type)