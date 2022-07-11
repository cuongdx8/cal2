from requests import Session

from app.users import users_dao
from app.users.users import User
from app.users.profiles.profiles import Profile
from app.exception import ValidateError
from app.exception.auth_exception import InvalidPasswordException
from app.utils import validate_utils, password_utils


def info(sub: int, session: Session) -> User:
    account = users_dao.find_by_id(sub, session)
    account.password = None
    account.active_flag = None
    account.credentials = None
    account.created_at = None
    account.updated_at = None
    return account


def get_profile(username: str, session: Session) -> Profile:
    account = users_dao.find_by_username(username, session)
    return account.profile


def find_by_id(sub: int, session: Session) -> User:
    return users_dao.find_by_id(sub, session)


def update_profile(sub: int, profile: Profile, session: Session) -> User:
    account = users_dao.find_by_id(sub, session)
    account.profile.update(profile)
    users_dao.add(account, session)
    return account


def change_password(sub, old_password, new_password, session) -> User:
    account = users_dao.find_by_id(sub, session)
    if password_utils.compare_password(old_password, account.password):
        account.password = password_utils.encode_password(new_password)

        users_dao.add(account, session)
        return account
    else:
        raise InvalidPasswordException


def validate_change_password(old_password, new_password):
    if not old_password or not new_password:
        raise ValidateError('Not found required fields: old_password, new_password')
    validate_utils.password(new_password)


def validate_update_profile(profile):
    # TODO validate profiles
    return None
