import json

import flask
from flask import Blueprint, Response, jsonify, request
from sqlalchemy.orm import Session

from app.account.account import Account
from app.auth import auth_services
from app.constants import Constants
from app.exception import JWTError
from app.exception.auth_exception import UsernameOrEmailInvalidException, ActiveAccountException, UserNotFoundException, \
    InvalidCredentialsException, EmailNotFoundException
from app.schemas import account_schema
from app.utils import jwt_utils, gg_utils, fb_utils
from app.utils.database_utils import transaction, connection

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')


@bp_auth.route('/register', methods=['POST'])
@transaction
def register(session: Session):
    """
    Register endpoint
    ---
    tags:
      - auth
    parameters:
      - name: Register Body
        in: body
        required: false
        schema:
          id: Account
          required:
            - email
            - username
            - password
          properties:
            email:
              type: string
            username:
              type: string
            password:
              type: string
            profile:
              type: object
              properties:
                full_name:
                    type: string
                avatar:
                    type: string
                description:
                    type: string
                language:
                    type: string
                timezone:
                    type: string
                time_format:
                    type: string
                first_day_of_week:
                    type: string
    responses:
      200:
        description: The account inserted in the database with active_flag = False
        schema:
          properties:
            type:
              type: string
            email:
              type: string
            username:
              type: string
            active_flag:
              type: boolean
              default: False
            created_at:
              type:
            profile:
              type: object
              properties:
                full_name:
                    type: string
                avatar:
                    type: string
                description:
                    type: string
                language:
                    type: string
                timezone:
                    type: string
                time_format:
                    type: string
                first_day_of_week:
                    type: string
      409:
        description: Username or email is existing in database
    """
    try:
        data = request.get_json()
        auth_services.validate_register(data, session)
        account = account_schema.load(data)
        account.type = Constants.ACCOUNT_TYPE_LOCAL
        account = auth_services.register(account, session)
        return Response(account_schema.dump(account), status=200)
    except UsernameOrEmailInvalidException:
        return Response('Username or email is invalid')
    except Exception as err:
        raise err


@bp_auth.route('/login', methods=['POST'])
@connection
def login(session: Session):
    """
    Login endpoint
    ---
    tags:
        - auth
    parameters:
        - name: login
          in: body
          description: Login info
          schema:
            type: object
            required:
                - password
            properties:
                username:
                    type: string
                email:
                    type: string
                password:
                    type: string
    responses:
        200:
            description: Login success
            schema:
                type: object
                properties:
                    token:
                        type: string
        404:
            description: Username or password is invalid
    """
    try:
        data = request.get_json()
        auth_services.validate_login(data)
        result = auth_services.login(data, session)
        return Response(json.dumps(result), status=200)
    except InvalidCredentialsException as err:
        return Response('Username or password is invalid', status=404)
    except Exception as err:
        raise err


@bp_auth.route('/google', methods=['GET'])
def login_gg():
    """
    Get url login with google
    ---
    tags:
        - auth
    responses:
        302:
            description: Redirect to google consent
    """
    return flask.redirect(gg_utils.generate_url_login())


@bp_auth.route('/google-callback', methods=['GET'])
@transaction
def login_gg_callback(session: Session):
    """
    Login with google callback
    ---
    tags:
        - auth
    responses:
        200:
            description: Login success
            schema:
                type: object
                properties:
                    token:
                        type: string
    """
    try:
        credentials = json.loads(gg_utils.request_exchange_code(request.args.get('code')))
        account = auth_services.register(Account(credentials=credentials, type=Constants.ACCOUNT_TYPE_GOOGLE), session)
        return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
    except Exception as err:
        raise err


@bp_auth.route('/facebook', methods=['GET'])
def login_fb():
    """
    Get url login facebook
    ---
    tags:
        - auth
    responses:
        302:
            description: Redirect to facebook
    :return:
    """
    return flask.redirect(fb_utils.generate_url_login(None))


@bp_auth.route('/facebook-callback', methods=['GET'])
@transaction
def facebook_login_callback(session: Session):
    """
    Login with facebook callback
    ---
    tags:
        - auth
    responses:
        200:
            description: Login success
            schema:
                type: object
                properties:
                    token:
                        type: string
    """

    try:
        credentials = json.loads(fb_utils.request_exchange_code(request.args.get('code')))
        account = auth_services.register(Account(credentials=credentials, type=Constants.ACCOUNT_TYPE_FACEBOOK), session)
        session.flush()
        return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
    except Exception as err:
        raise err


@bp_auth.route('/forgot-password', methods=['GET', 'POST'])
@transaction
def forgot_password(session):
    try:
        auth_services.validate_forgot_password(request)
        if request.method == Constants.GET_METHOD:
            auth_services.forgot_password(request.args.get('email'), session)
            return Response(status=200)
        else:
            try:
                data = request.get_json()
                sub = jwt_utils.get_payload(request.headers['Authorization'][7:]).get('sub')
                account = auth_services.change_password(sub, data.get('password'), session)
                return Response(json.dumps({'token': jwt_utils.create_access_token(account)}), status=200)
            except UserNotFoundException:
                return Response('Not found user with id', status=404)
            except JWTError:
                return Response("'Invalid JWT', 'User does not exist'", status=401)
    except EmailNotFoundException:
        return Response('EmailNotFoundException', status=404)


@bp_auth.route('/active')
@transaction
def verify_email(session: Session):
    """
    Verify email end point
    ---
    tags:
        - auth
    parameters:
        - name: token
          in: query
          required: True
    response:
        200:
            description: Active account is successful

    """
    try:
        token = request.args.get('token')
        sub = jwt_utils.get_payload(token).get('sub')
        try:
            auth_services.active_account(sub, session=session)
            return Response(status=200)
        except ActiveAccountException as err:
            return Response(status=400)
        except UserNotFoundException as err:
            return Response(status=404)
    except JWTError:
        return Response('Token is expired', status=400)
    except Exception as err:
        raise err


@bp_auth.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint returning a list of colors by palette
    This is using docstrings for specifications.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cyan', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)
