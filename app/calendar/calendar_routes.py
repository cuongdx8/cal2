import json

from flask import Blueprint, Response, request
from sqlalchemy.orm import Session

from app.account import account_services
from app.calendar import calendar_services
from app.schemas import calendar_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import connection, transaction

bp_calendar = Blueprint('calendar', __name__, url_prefix='/calendar')


@bp_calendar.route('/me', methods=['GET'])
@verify
@connection
def me(payload: dict, session: Session) -> Response:
    try:
        account = account_services.find_by_id(payload.get('sub'), session)
        calendars = []
        for item in account.linked_accounts:
            calendars.extend([association.calendar for association in item.association_calendars])
        result = [calendar_schema.dumps(item) for item in calendars]
        result = json.dumps(result)
        return Response(result, status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['GET'])
@verify
@transaction
def get_by_id(payload: dict, calendar_id: int, session: Session) -> Response:
    try:
        if calendar_services.can_read(payload.get('sub'), calendar_id, session):
            calendar = calendar_services.find_by_id(calendar_id, session)
            return Response(calendar_schema.dumps(calendar), status=200)
        else:
            return Response('Not found', status=404)
    except Exception as err:
        raise err


@bp_calendar.route('', methods=['POST'])
@verify
@transaction
def create_calendar(payload: dict, session: Session) -> Response:
    try:
        calendar_services.validate_create(payload.get('sub'), request.get_json(), session)
        calendar = calendar_services.create(data=request.get_json(), session=session)
        return Response(calendar_schema.dumps(calendar), status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['PATCH'])
@verify
@transaction
def update_calendar(payload, calendar_id, session):
    # Only update calendar's name
    try:
        calendar_services.validate_update(payload.get('sub'), calendar_id, request.get_json(), session)
        calendar = calendar_services.update(sub=payload.get('sub'), calendar_id=calendar_id, data=request.get_json(), session=session)
        return Response(json.dumps(calendar), status=200)
    except Exception as err:
        raise err


@bp_calendar.route('/<calendar_id>', methods=['DELETE'])
@verify
@transaction
def delete_calendar_or_clear(payload, calendar_id, session):
    try:
        calendar_services.validate_delete(sub=payload.get('sub'), calendar_id=calendar_id, connection_id=request.args.get('connection_id'), session=session)
        calendar_services.delete(sub=payload.get('sub'), calendar_id=calendar_id, connection_id=request.args.get('connection_id'), session=session)
        return Response(status=200)
    except Exception as err:
        raise err
