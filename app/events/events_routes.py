import json

from flask import Blueprint, Response, request
from requests import Session

from app.constants import Constants
from app.events import events_services
from app.schemas import events_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import connection, transaction

bp_event = Blueprint('events', __name__, url_prefix='/events')


@bp_event.route('/<events_id>', methods=['GET'])
@verify
@connection
def get_by_id(payload: dict, events_id: int, session: Session) -> Response:
    try:
        events_services.validate_get_by_id(sub=payload.get('sub'), event_id=events_id, session=session)
        event = events_services.find_by_id(event_id=events_id, session=session)
        return Response(events_schema.dumps(event), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_event.route('/', methods=['POST'])
@verify
@transaction
def create_event(payload: dict, session: Session) -> Response:
    try:
        events_services.validate_create_event(sub=payload.get('sub'), data=request.get_json(), session=session)
        event = events_services.create_event(sub=payload.get('sub'), data=request.get_json(), session=session)
        return Response(events_schema.dumps(event), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


@bp_event.route('/<events_id>', methods=['PATCH'])
@verify
@transaction
def update_event(payload: dict, events_id: int, session: Session) -> Response:
    try:
        event = events_services.find_by_id(events_id, session)
        events_services.validate_update(sub=payload.get('sub'), event=event, data=request.get_json(), session=session)
        event = events_services.update_event(sub=payload.get('sub'), event=event, data=request.get_json(), session=session)
        return Response(events_schema.dumps(event), content_type=Constants.CONTENT_TYPE_JSON, status=200)
    except Exception as err:
        raise err


# @bp_event.route('/<events_id>', methods=['DELETE'])
# @verify
# @transaction
# def delete_event(payload: dict, events_id: int, session: Session) -> Response:
#     try:
#         events = events_services.find_by_id(events_id, session)
#         events_services.validate_delete(sub=payload.get('sub'), events_id=events_id)
#         events_services.delete(sub=payload.get('sub'), events_id=events_id)
#         return Response(status=204)
#     except Exception as err:
#         raise err