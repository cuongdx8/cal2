import datetime
import json

import flask
import jwt
from sqlalchemy.orm import Session

from app.account import account_dao
from app.account.account import Account
from app.association import ConnectionCalendar
from app.auth import auth_dao
from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.constants import Constants
from app.exception import ValidateError, NotFoundFieldsException
from app.exception.auth_exception import UsernameOrEmailInvalidException, ActiveAccountException, \
    UserNotFoundException, InvalidCredentialsException, EmailNotFoundException
from app.account.profile.profile import Profile
from app.utils import password_utils, mail_utils, jwt_utils, fb_utils, validate_utils


def validate_register(data: dict, session: Session) -> None:
    if not set(('username', 'email', 'password')).issubset(set(data.keys())):
        raise ValidateError('Username, email and password are required')
    if auth_dao.is_username_or_email_existing(data.get('username'), data.get('email'), session):
        raise UsernameOrEmailInvalidException
    # TODO validate fields value


def validate_login(data: dict):
    if 'password' not in data or ('username' not in data and 'email' not in data):
        raise ValidateError('Username or email and password are required')


def register(account: Account, session: Session) -> Account:
    account = init_account(account)
    if account.type == Constants.ACCOUNT_TYPE_LOCAL:
        db_account = account_dao.find_by_email(account.email, session)
    else:
        db_account = account_dao.find_by_platform_id_and_type(account.platform_id, account.type, session)
    if db_account:
        db_account.update(account)
    else:
        db_account = account
        db_account.created_at = datetime.datetime.utcnow()
    db_account.updated_at = datetime.datetime.utcnow()
    account_dao.add(db_account, session=session)
    if account.type == Constants.ACCOUNT_TYPE_LOCAL:
        mail_utils.send_mail_verify_email(db_account)
    return db_account


def init_account(account):
    profile_default = Profile(avatar=Constants.PROFILE_DEFAULT_AVATAR,
                              description=Constants.PROFILE_DEFAULT_DESCRIPTION,
                              language=Constants.PROFILE_DEFAULT_LANGUAGE,
                              timezone=Constants.PROFILE_DEFAULT_TIMEZONE,
                              time_format=Constants.PROFILE_DEFAULT_TIMEFORMAT,
                              first_day_of_week=Constants.PROFILE_DEFAULT_FIRST_DAY_OF_WEEK)
    match account.type:
        case Constants.ACCOUNT_TYPE_LOCAL:
            account = account
            account.active_flag = False
            account.type = Constants.ACCOUNT_TYPE_LOCAL

            # Profile
            if not account.profile:
                profile = profile_default
                account.profile = profile
            account.updated_at = datetime.datetime.utcnow()
            account.password = password_utils.encode_password(account.password)

        case Constants.ACCOUNT_TYPE_GOOGLE:
            credentials = account.credentials
            payload = jwt.decode(credentials.get('id_token'), options={"verify_signature": False})
            account.email = account.username = payload.get('email')
            account.platform_id = payload.get('sub')
            account.type = Constants.ACCOUNT_TYPE_GOOGLE
            account.active_flag = True

            # Profile
            profile_default.avatar = payload.get('picture')
            profile_default.full_name = payload.get('name')
            account.profile = profile_default
        case Constants.ACCOUNT_TYPE_FACEBOOK:
            user_info = json.loads(fb_utils.get_user_info(account.credentials.get('access_token')))

            account.active_flag = True
            account.type_account = Constants.ACCOUNT_TYPE_FACEBOOK
            account.platform_id = user_info.get('id')

            profile = Profile()
            profile.name = user_info.get('name')

            account.profile = profile
    primary_connection = Connection()
    calendar = Calendar()
    association = ConnectionCalendar()

    primary_connection.type = calendar.type = Constants.ACCOUNT_TYPE_LOCAL
    calendar.summary = primary_connection.email = primary_connection.username = account.email
    calendar.created_at = calendar.updated_at = primary_connection.created_at = primary_connection.updated_at \
        = datetime.datetime.utcnow()
    calendar.timezone = account.profile.timezone

    association.calendar = calendar
    association.connection = primary_connection

    primary_connection.association_calendars = [association]
    account.connections = [primary_connection]

    return account


def login(data: dict, session: Session) -> dict:
    if data.get('email'):
        account = account_dao.find_by_email(data.get('email'), session)
    else:
        account = account_dao.find_by_username(data.get('username'), session)
    if password_utils.compare_password(data.get('password'), account.password):
        return {'token': jwt_utils.create_access_token(account)}
    else:
        raise InvalidCredentialsException


def active_account(sub: str, session: Session) -> None:
    account = account_dao.find_by_id(sub, session=session)
    if not account:
        raise UserNotFoundException
    if account.active_flag:
        raise ActiveAccountException
    account.active_flag = True
    account_dao.add(account, session)


def forgot_password(email, session):
    account = account_dao.find_by_email_and_platform(email=email, type=Constants.ACCOUNT_TYPE_LOCAL, session=session)
    if account:
        mail_utils.send_mail_forgot_password(account)
    else:
        raise EmailNotFoundException


def validate_forgot_password(request: flask.Request):
    if request.method == Constants.GET_METHOD:
        if not request.args.get('email'):
            raise NotFoundFieldsException('email')
    else:
        validate_utils.password(request.get_json().get('password'))


def change_password(sub: str, password: str, session: Session):
    account = account_dao.find_by_id(sub, session)
    if account:
        account.password = password_utils.encode_password(password)
        account_dao.add(account, session)
        return account
    else:
        raise UserNotFoundException
