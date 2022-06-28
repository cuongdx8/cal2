import datetime

from sqlalchemy.orm import Session

from app.account import account_dao
from app.account.account import Account
from app.auth import auth_dao
from app.constants import Constants
from app.exception import ValidateError
from app.exception.auth_exception import UsernameOrEmailInvalidException, ActiveAccountException, UserNotFoundException, \
    InvalidCredentialsException
from app.profile.profile import Profile
from app.utils import password_utils, mail_utils, jwt_utils


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
    db_account = account_dao.find_by_email(account.email, session)
    if db_account:
        db_account.update(account)
    else:
        db_account = account
        db_account.active_flag = False
        db_account.type = Constants.ACCOUNT_TYPE_LOCAL
        db_account.created_at = datetime.datetime.utcnow()
        if not db_account.profile:
            profile = Profile(avatar=Constants.PROFILE_DEFAULT_AVATAR,
                              description=Constants.PROFILE_DEFAULT_DESCRIPTION,
                              language=Constants.PROFILE_DEFAULT_LANGUAGE,
                              timezone=Constants.PROFILE_DEFAULT_TIMEZONE,
                              time_format=Constants.PROFILE_DEFAULT_TIMEFORMAT,
                              first_day_of_week=Constants.PROFILE_DEFAULT_FIRST_DAY_OF_WEEK)
            db_account.profile = profile
    db_account.updated_at = datetime.datetime.utcnow()
    db_account.password = password_utils.encode_password(account.password)
    account_dao.add(db_account, session=session)
    mail_utils.send_mail_verify_email(db_account)

    return db_account


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
