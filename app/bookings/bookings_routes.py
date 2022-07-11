import json

from flask import Blueprint, Response, request
from sqlalchemy.orm import Session

from app.bookings import bookings_services
from app.bookings.availabilitys import availability_services
from app.bookings.booking_types import booking_types_services
from app.constants import Constants
from app.schemas import booking_availability_schema, booking_type_schema, booking_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import transaction

bp_booking = Blueprint('bookings', __name__, url_prefix='/bookings')


@bp_booking.route('/availability', methods=['GET'])
@verify
@transaction
def get_all_booking_availability(payload: dict, session: Session):
    try:
        availabilities = availability_services.find_by_account_id(sub=payload.get('sub'), session=session)
        result = [booking_availability_schema.dump(item) for item in availabilities]
        return Response(json.dumps(result), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/availability/<availability_id>', methods=['GET'])
@verify
@transaction
def get_availability_by_id(payload: dict, availability_id: int, session: Session):
    try:
        availability = availability_services.find_by_id(availability_id, session)
        if availability.account_id != int(payload.get('sub')):
            raise PermissionError('You don\'t have any availabilitys with id=: {}'.format(availability_id))
        return Response(booking_availability_schema.dumps(availability), content_type=Constants.CONTENT_TYPE_JSON,
                        status=200)
    except Exception as err:
        raise err


@bp_booking.route('/availability', methods=['POST'])
@verify
@transaction
def create_booking_availability(payload: dict, session: Session):
    try:
        availability_services.validate_create(data=request.get_json())
        availability = availability_services.create(sub=payload.get('sub'), data=request.get_json(), session=session)
        return Response(booking_availability_schema.dumps(availability), content_type=Constants.CONTENT_TYPE_JSON,
                        status=200)
    except Exception as err:
        raise err


@bp_booking.route('/availability/<availability_id>', methods=['PATCH'])
@verify
@transaction
def update_booking_availability(payload: dict, availability_id: int, session: Session):
    try:
        availability_services.validate_update(data=request.get_json())
        availability = availability_services.update(sub=payload.get('sub'), availability_id=availability_id,
                                                    data=request.get_json(), session=session)
        return Response(booking_availability_schema.dumps(availability), content_type=Constants.CONTENT_TYPE_JSON,
                        status=200)
    except Exception as err:
        raise err


@bp_booking.route('/availability/<availability_id>', methods=['DELETE'])
@verify
@transaction
def delete_booking_availability(payload: dict, availability_id: int, session: Session):
    try:
        availability = availability_services.find_by_id(availability_id, session)
        if availability.account_id == int(payload.get('sub')):
            availability_services.delete(availability, session)
        else:
            raise PermissionError('You don\'t have any availabilitys with id=: {}'.format(availability_id))
    except Exception as err:
        raise err


@bp_booking.route('/availability/default/<availability_id>', methods=['GET'])
@verify
@transaction
def set_availability_default(payload: dict, availability_id: int, session: Session) -> Response:
    try:
        availability = availability_services.find_by_id(availability_id, session)
        if availability.account_id == int(payload.get('sub')):
            availability_services.set_default(availability_id=availability_id, session=session)
        else:
            raise PermissionError('You don\'t have any availabilitys with id=: {}'.format(availability_id))
        return Response(booking_availability_schema.dumps(availability), content_type=Constants.CONTENT_TYPE_JSON,
                        status=200)
    except Exception as err:
        raise err


@bp_booking.route('/booking-type/me', methods=['GET'])
@verify
@transaction
def get_all_booking_type(payload: dict, session: Session) -> Response:
    try:
        booking_types = booking_type_services.me(sub=payload.get('sub'), session=session)
        return Response(json.dumps([booking_type_schema.dump(item) for item in booking_types]))
    except Exception as err:
        raise err


@bp_booking.route('/booking-type/<booking_type_id>', methods=['GET'])
@verify
@transaction
def get_booking_type_by_id(payload: dict, booking_type_id: int, session: Session):
    try:
        booking_type = booking_type_services.find_by_id(booking_type_id=booking_type_id, session=session)
        if booking_type.account_id != int(payload.get('sub')):
            raise PermissionError('You don\'t have any booking_types with id=: {}'.format(booking_type_id))
        return Response(booking_type_schema.dumps(booking_type), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/booking-type', methods=['POST'])
@verify
@transaction
def create_booking_type(payload: dict, session: Session) -> Response:
    try:
        booking_type_services.validate_create(data=request.get_json())
        booking_type = booking_type_services.create(sub=payload.get('sub'), data=request.get_json(), session=session)
        return Response(booking_type_schema.dumps(booking_type), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/booking-type/<booking_type_id>', methods=['PATCH'])
@verify
@transaction
def update_booking_type(payload: dict, booking_type_id: int, session: Session) -> Response:
    try:
        booking_type_services.validate_update(sub=payload.get('sub'), data=request.get_json())
        booking_type = booking_type_services.update(data=request.get_json(), session=session)
        return Response(booking_type_schema.dumps(booking_type), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/booking-type/<booking_type_id>', methods=['DELETE'])
@verify
@transaction
def delete_booking_type(payload: dict, booking_type_id: int, session: Session) -> Response:
    try:
        booking_type = booking_type_services.find_by_id(booking_type_id, session)
        if booking_type.account_id == int(payload.get('sub')):
            booking_type_services.delete(booking_type, session)
        else:
            raise PermissionError('You don\'t have any booking_types with id=: {}'.format(booking_type_id))
        return Response(status=204)
    except Exception as err:
        raise err


@bp_booking.route('/', methods=['GET'])
@verify
@transaction
def me(payload: dict, session: Session):
    try:
        bookings = bookings_services.me(sub=payload.get('sub'), session=session)
        return Response(json.dumps(booking_schema.dump(item) for item in bookings),
                        content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/<booking_id>', methods=['GET'])
@verify
@transaction
def get_booking_by_id(payload: dict, booking_id: int, session: Session) -> Response:
    try:
        booking = bookings_services.find_by_id(booking_id=booking_id, session=session)
        if booking.account_id != int(payload.get('sub')):
            raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
        return Response(booking_schema.dumps(booking), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/', method=['POST'])
@verify
@transaction
def create_booking(payload: dict, session: Session) -> Response:
    try:
        bookings_services.validate_create(data=request.get_json(), session=session)
        booking = bookings_services.create(sub=payload.get('sub'), data=request.get_json(), session=session)
        return Response(booking_schema.dumps(booking), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/<booking_id>', mehotds=['PATCH'])
@verify
@transaction
def update_booking(payload: dict, booking_id, session: Session) -> Response:
    try:
        db_booking = bookings_services.validate_update(sub=payload.get('sub'), booking_id=booking_id, data=request.get_json(), session=session)
        booking = bookings_services.update(booking=db_booking, data=request.get_json(), session=session)
        return Response(booking_schema.dumps(booking), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_booking.route('/<booking_id>', methods=['DELETE'])
@verify
@transaction
def delete_booking(payload: dict, booking_id: int, session: Session) -> Response:
    try:
        booking = bookings_services.find_by_id(booking_id, session)
        if booking.account_id != int(payload.get('sub')):
            raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
        bookings_services.delete(booking, session)
        return Response(status=204)
    except Exception as err:
        raise err


@bp_booking.route('/cancel/<booking_id>', methods=['GET'])
@verify
@transaction
def cancel(payload: dict, booking_id: int, session: Session):
    try:
        booking = bookings_services.find_by_id(booking_id, session)
        if int(payload.get('sub')) == booking.account_id:
            booking.cancelled_flag = True
            bookings_services.add(booking, session)
            return Response(status=200)
        else:
            raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
    except Exception as err:
        raise err


@bp_booking.route('/confirm/<booking_id>', methods=['GET'])
@verify
@transaction
def confirm(payload: dict, booking_id: int, session: Session):
    try:
        booking = bookings_services.find_by_id(booking_id, session)
        if int(payload.get('sub')) == booking.account_id and booking.confirm_flag is None:
            booking.confirm_flag = True
            bookings_services.add(booking, session)
            bookings_services.send_mail_confirm(booking)
            return Response(status=200)
        else:
            raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
    except Exception as err:
        raise err


@bp_booking.route('/rejected/<booking_id>', methods=['GET'])
@verify
@transaction
def rejected(payload: dict, booking_id: int, session: Session):
    try:
        booking = bookings_services.find_by_id(booking_id, session)
        if int(payload.get('sub')) == booking.account_id and booking.confirm_flag is None:
            booking.confirm_flag = False
            bookings_services.add(booking, session)
            bookings_services.send_mail_confirm(booking)
            return Response(status=200)
        else:
            raise PermissionError('You don\'t have any bookings with id=: {}'.format(booking_id))
    except Exception as err:
        raise err


@bp_booking.route('/public/<account_id>/booking-type', methods=['GET'])
@transaction
def public_booking_type_resource(account_id: int, session: Session):
    try:
        booking_types = booking_type_services.me(sub=account_id, session=session)
        return Response(json.dumps([booking_type_schema.dump(item) for item in booking_types]), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err