import json

import flask
from flask import Blueprint, Response, request
from sqlalchemy.orm import Session

from app.users.users import User
from app.auths import auths_services
from app.constants import Constants
from app.exception import JWTError
from app.exception.auth_exception import UsernameOrEmailInvalidException, ActiveAccountException, UserNotFoundException, \
    InvalidCredentialsException, EmailNotFoundException
from app.schemas import users_schema
from app.utils import jwt_utils, gg_utils, fb_utils
from app.utils.database_utils import transaction, connection

bp_auth = Blueprint('auths', __name__, url_prefix='/auths')


@bp_auth.route('/register', methods=['POST'])
@transaction
def register(session: Session):
    try:
        data = request.get_json()
        auths_services.validate_register(data, session)
        account = users_schema.load(data)
        account.type = Constants.ACCOUNT_TYPE_LOCAL
        auths_services.register(account, session)
        return Response(status=200)
    except UsernameOrEmailInvalidException:
        return Response('Username or email is invalid', status=400)
    except Exception as err:
        raise err


@bp_auth.route('/login', methods=['POST'])
@connection
def login(session: Session):
    try:
        auths_services.validate_login(request.get_json())
        result = auths_services.login(request.get_json(), session)
        return Response(json.dumps(result), status=200, content_type='application/json')
    except InvalidCredentialsException as err:
        return Response('Username or password is invalid', status=404)
    except Exception as err:
        raise err


@bp_auth.route('/google', methods=['GET'])
def login_gg():
    return flask.redirect(gg_utils.generate_url_login())


@bp_auth.route('/google-callback', methods=['GET'])
@transaction
def login_gg_callback(session: Session):
    try:
        credentials = gg_utils.request_exchange_code(request.args.get('code'))
        account = auths_services.register(User(credentials=credentials, type=Constants.ACCOUNT_TYPE_GOOGLE), session)
        session.flush()
        return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
    except Exception as err:
        raise err


@bp_auth.route('/facebook', methods=['GET'])
def login_fb():
    return flask.redirect(fb_utils.generate_url_login(None))


@bp_auth.route('/facebook-callback', methods=['GET'])
@transaction
def facebook_login_callback(session: Session):
    try:
        credentials = json.loads(fb_utils.request_exchange_code(request.args.get('code')))
        account = auths_services.register(User(credentials=credentials, type=Constants.ACCOUNT_TYPE_FACEBOOK), session)
        session.flush()
        return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
    except Exception as err:
        raise err


@bp_auth.route('/forgot-password', methods=['GET', 'POST'])
@transaction
def forgot_password(session):
    try:
        auths_services.validate_forgot_password(request)
        if request.method == Constants.GET_METHOD:
            auths_services.forgot_password(request.args.get('email'), session)
            return Response(status=200)
        else:
            try:
                data = request.get_json()
                sub = jwt_utils.get_payload(request.args.get('token')).get('sub')
                account = auths_services.change_password(sub, data.get('password'), session)
                return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
            except UserNotFoundException:
                return Response('Not found users with id', status=404)
            except JWTError:
                return Response("'Invalid JWT', 'User does not exist'", status=401)
    except EmailNotFoundException:
        return Response('EmailNotFoundException', status=404)


@bp_auth.route('/active')
@transaction
def verify_email(session: Session):
    try:
        token = request.args.get('token')
        sub = jwt_utils.get_payload(token).get('sub')
        try:
            auths_services.active_account(sub, session=session)
            return Response(status=200)
        except ActiveAccountException as err:
            return Response(status=400)
        except UserNotFoundException as err:
            return Response(status=404)
    except JWTError:
        return Response('Token is expired', status=400)
    except Exception as err:
        raise err
