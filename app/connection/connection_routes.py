import json

import requests
from flask import Blueprint, Response, request
from sqlalchemy.orm import Session
from werkzeug.utils import redirect

from app.connection import connection_services
from app.connection.connection import Connection
from app.constants import Constants
from app.utils import gg_utils, mic_utils
from app.utils.authorization_utils import verify
from app.utils.database_utils import transaction

bp_connection = Blueprint('connection', __name__, url_prefix='/connection')


@bp_connection.route('/google', methods=['GET'])
@verify
def connect_google(payload: dict):
    return redirect(gg_utils.generate_url_login(state=payload.get('sub'), connect_calendar=True))


@bp_connection.route('/google-callback', methods=['GET'])
@transaction
def connect_google_callback(session: Session):
    try:
        credentials = gg_utils.request_exchange_code(code=request.args.get('code'), connect_calendar=True)
        connection_services.connect(request.args.get('state'), Connection(credentials=credentials,
                                                                          type=Constants.ACCOUNT_TYPE_GOOGLE),
                                    session)
        return Response(status=200)
    except Exception as err:
        raise err


@bp_connection.route('/outlook')
@verify
def linked_outlook(payload):
    authorization_url = mic_utils.generate_url_login(payload.get('sub'))
    return redirect(authorization_url)


@bp_connection.route('/outlook-callback')
@transaction
def outlook_callback(session):
    try:
        sub = request.args.get('state')
        credentials = mic_utils.request_exchange_code(code=request.args.get('code'))

        connection_services.connect(request.args.get('state'), Connection(credentials=credentials,
                                                                          type=Constants.ACCOUNT_TYPE_MICROSOFT),
                                    session)
        # load linked_account from cloud
        linked_account = linked_account_services.load_microsoft_linked_account(credentials)
        account = account_services.find_by_id(sub, session)

        # if linked_account exists in database
        db_linked_account = linked_account_services.find_by_supplier_id_platform(linked_account.supplier_id,
                                                                                 linked_account.platform, session)
        if db_linked_account:
            if account in db_linked_account.accounts:
                # Linked_account is connected account cause conflict
                return Response('Conflict', status=409)
            else:
                # Linked_account is existing in db, but isn't connect to this account
                db_linked_account.accounts.append(account)
                linked_account_services.add(db_linked_account, session)
                return Response('Success!', status=200)

        linked_account_calendars = calendar_services.load_mic_calendar_by_linked_account(linked_account, session)
        linked_account.association_calendars = linked_account_calendars
        for item in linked_account_calendars:
            calendar = item.calendar
            if calendar.id is not None:
                continue
            events = event_services.load_mic_events_by_calendar(calendar, linked_account=linked_account)
            calendar.events = events

        account.linked_accounts.append(linked_account)
        linked_account_services.add(linked_account, session)
        session.flush()
        channel_notification_services.create_by_linked_account(linked_account, session)
        return Response('Success!', status=200)
    except Exception as error:
        raise error




@bp_connection.route('/<connection_id>', methods=['DELETE'])
@verify
@transaction
def disconnect(payload: dict, connection_id: str, session: Session):
    try:
        connection_services.validate_disconnect(sub=payload.get('sub'), connection_id=connection_id, session=session)
        connection_services.disconnect(sub=payload.get('sub'), connection_id=connection_id, session=session)
        return Response(status=200)
    except Exception as err:
        raise err
