from requests import Session

from app.account import account_dao
from app.account.account import Account
from app.account.profile.profile import Profile
from app.exception import ValidateError
from app.exception.auth_exception import InvalidPasswordException
from app.utils import validate_utils, password_utils


def update(account: Account, other: Account):
    pass


def info(sub, session):
    account = account_dao.find_by_id(sub, session)
    account.password = None
    account.active_flag = None
    account.credentials = None
    account.created_at = None
    account.updated_at = None
    return account


def get_profile(username: str, session: Session):
    account = account_dao.find_by_username(username, session)
    return account.profile


def find_by_id(sub: str, session: Session):
    return account_dao.find_by_id(sub, session)


def update_profile(sub: str, profile: Profile, session: Session) -> Account:
    account = account_dao.find_by_id(sub, session)
    account.profile.update(profile)
    account_dao.add(account, session)
    return account


def change_password(sub, old_password, new_password, session):
    account = account_dao.find_by_id(sub, session)
    if password_utils.compare_password(old_password, account.password):
        account.password = password_utils.encode_password(new_password)

        account_dao.add(account)
        return account
    else:
        raise InvalidPasswordException


def validate_change_password(old_password, new_password):
    if not old_password or not new_password:
        raise ValidateError('Not found required fields: old_password, new_password')
    validate_utils.password(new_password)


def validate_update_profile(profile):
    # TODO validate profile
    return None