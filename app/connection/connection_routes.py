import json

from flask import Blueprint, Response, request
from sqlalchemy.orm import Session
from werkzeug.utils import redirect

from app.connection import connection_services
from app.connection.connection import Connection
from app.constants import Constants
from app.utils import gg_utils, jwt_utils
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
        credentials = json.loads(gg_utils.request_exchange_code(code=request.args.get('code'), connect_calendar=True))
        connection_services.connect(request.args.get('state'), Connection(credentials=credentials,
                                                                          type=Constants.ACCOUNT_TYPE_GOOGLE),
                                    session)
        return Response(status=200)
    except Exception as err:
        raise err
