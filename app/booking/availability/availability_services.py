from typing import List

from sqlalchemy.orm import Session

from app.booking.availability import availability_dao
from app.booking.availability.availability import Availability
from app.constants import Constants
from app.exception import ValidateError
from app.schemas import booking_availability_schema
from app.utils import validate_utils


def find_by_account_id(sub: int, session: Session) -> List[Availability]:
    return availability_dao.find_by_account_id(sub=sub, session=session)


def find_by_id(availability_id: int, session: Session) -> Availability:
    return availability_dao.find_by_id(availability_id=availability_id, session=session)


def validate_create(data):
    validate_utils.validate_required_field(data, *Constants.CREATE_SCHEDULE_FIELDS_REQUIRED)
    validate_utils.naming_convention(data.get('name'))
    validate_utils.validate_time_by_week_days(data.get('time_by_week_days'))
    validate_utils.validate_timezone(data.get('timezone'))


def create(sub, data, session):
    availability = booking_availability_schema(data)
    availability.account_id = sub
    if not availability.default_flag:
        availability.default_flag = False
    availability_dao.add(availability=availability, session=session)
    return availability


def set_default(availability_id: int, session: Session):
    return availability_dao.set_default(availability_id=availability_id, session=session)


def delete(availability: Availability, session: Session):
    return availability_dao.delete(availability=availability, session=session)


def validate_update(data):
    if data.get('name'):
        validate_utils.naming_convention(data.get('name'))
    if data.get('time_by_week_days'):
        validate_utils.validate_time_by_week_days(data.get('time_by_week_days'))
    if data.get('timezone'):
        validate_utils.validate_timezone(data.get('timezone'))
    if data.get('default_flag'):
        raise ValidateError('Don\'t use update to set default')
    if data.get('account_id'):
        raise ValidateError('Dont\'t allow update account_id')


def update(sub, availability_id, data, session):
    availability = availability_dao.find_by_id(availability_id, session)
    if availability.account_id != int(sub):
        raise ValidateError('Dont\'t allow update the availability_id = {}'.format(availability_id))
    availability.update(booking_availability_schema.load(data))
    availability_dao.update(availability, session)


