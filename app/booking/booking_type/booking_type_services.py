from sqlalchemy.orm import Session

from app.booking.booking_type import booking_type_dao
from app.booking.booking_type.booking_type import BookingType
from app.schemas import booking_type_schema


def me(sub: int, session: Session):
    return booking_type_dao.me(sub=sub, session=session)


def find_by_id(booking_type_id: int, session: Session):
    return booking_type_dao.find_by_id(booking_type_id=booking_type_id, session=session)


def delete(booking_type: BookingType, session: Session):
    return booking_type_dao.delete(booking_type, session)


def validate_update(sub: int, data: dict):
    return None


def update(booking_type_id: int, data: dict, session: Session) -> BookingType:
    booking_type = booking_type_dao.find_by_id(booking_type_id=booking_type_id, session=session)
    booking_type.update(booking_type_schema.load(data))
    booking_type_dao.update(booking_type, session)
    return booking_type


def validate_create(data):
    return None


def create(sub: int, data: dict, session: Session) -> BookingType:
    booking_type = booking_type_schema.load(data)
    booking_type.account_id = sub
    booking_type_dao.add(booking_type, session)
    return booking_type