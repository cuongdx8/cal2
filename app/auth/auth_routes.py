import json

from flask import Blueprint, Response, jsonify, request
from sqlalchemy.orm import Session

from app.auth import auth_services
from app.exception import JWTError
from app.exception.auth_exception import UsernameOrEmailInvalidException, ActiveAccountException, UserNotFoundException, \
    InvalidCredentialsException
from app.schemas import account_schema
from app.utils import jwt_utils
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
        account = auth_services.register(account, session)
        return Response(account_schema.dump(account), status=200)
    except UsernameOrEmailInvalidException :
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