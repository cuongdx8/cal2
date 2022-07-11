import json

from flask import Blueprint, Response, request
from sqlalchemy.orm import Session

from app.calendars import calendars_service
from app.constants import Constants
from app.schemas import calendars_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import connection, transaction

bp_calendar = Blueprint('calendars', __name__, url_prefix='/calendars')


@bp_calendar.route('/me', methods=['GET'])
@verify
@connection
def get_by_account_id(payload: dict, session: Session) -> Response:
    try:
        calendars = calendars_services.find_by_account_id(sub=payload.get('sub'), session=session)
        result = [calendars_schema.dump(item) for item in calendars]
        return Response(json.dumps(result), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/connection/<connection_id>', methods=['GET'])
@verify
@connection
def get_by_connection_id(payload: dict, connection_id: int, session: Session) -> Response:
    try:
        calendars_services.validate_find_by_connection_id(sub=payload.get('sub'), connection_id=connection_id,
                                                          session=session)
        calendars = calendars_services.find_by_connection_id(connection_id=connection_id, session=session)
        result = [calendars_schema.dump(item) for item in calendars]
        return Response(json.dumps(result), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['GET'])
@verify
@transaction
def get_by_id(payload: dict, calendar_id: int, session: Session) -> Response:
    try:
        if calendars_services.can_read(payload.get('sub'), calendar_id, session):
            calendar = calendars_services.find_by_id(calendar_id, session)
            return Response(calendars_schema.dumps(calendar), status=200)
        else:
            return Response('Not found', status=404)
    except Exception as err:
        raise err


@bp_calendar.route('', methods=['POST'])
@verify
@transaction
def create_calendar(payload: dict, session: Session) -> Response:
    try:
        calendars_services.validate_create(payload.get('sub'), request.get_json(), session)
        calendar = calendars_services.create(data=request.get_json(), session=session)
        return Response(calendars_schema.dumps(calendar), status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['PATCH'])
@verify
@transaction
def patch_calendar(payload, calendar_id, session):
    try:
        calendars_services.validate_patch(payload.get('sub'), calendar_id, request.get_json(), session)
        calendar = calendars_services.patch(sub=payload.get('sub'), calendar_id=calendar_id, data=request.get_json(),
                                            session=session)
        return Response(json.dumps(calendars_schema.dump(calendar)), content_type=Constants.CONTENT_TYPE_JSON,
                        status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['DELETE'])
@verify
@transaction
def delete_calendar_or_clear(payload, calendar_id, session):
    try:
        calendars_services.validate_delete(sub=payload.get('sub'), calendar_id=calendar_id,
                                           connection_id=request.args.get('connection_id'), session=session)
        calendars_services.delete(sub=payload.get('sub'), calendar_id=calendar_id,
                                  connection_id=request.args.get('connection_id'), session=session)
        return Response(status=200)
    except Exception as err:
        raise err
