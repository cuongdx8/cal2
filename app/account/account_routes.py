from flask import Blueprint, Response, request
from requests import Session

from app.account import account_services
from app.account.profile import profile_schema
from app.schemas import account_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import connection, transaction

bp_account = Blueprint('account', __name__, url_prefix='/account')


@bp_account.route('/me', methods=['GET'])
@verify
@connection
def me(payload: dict, session: Session):
    try:
        account = account_services.info(sub=payload.get('sub'), session=session)
        return Response(account_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_account.route('/change_password', methods=['POST'])
@verify
@transaction
def change_password(payload, session):
    try:
        data = request.get_json()
        # account_services.validate_update_profile()
        account_services.validate_change_password(old_password=data.get('old_password'),
                                                  new_password=data.get('new_password'))
        account = account_services.change_password(sub=payload.get('sub'), old_password=data.get('old_password'),
                                                   new_password=data.get('new_password'), session=session)
        return Response(account_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_account.route('/{username}/profile', methods=['GET'])
@connection
def get_profile(username: str, session: Session):
    try:
        account = account_services.get_profile(username=username, session=session)
        return Response(account_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_account.route('/profile', methods=['PATCH'])
@verify
@transaction
def update_profile(payload, session):
    try:
        data = request.get_json()
        # account_services.validate_update_profile()
        profile = profile_schema.load(data)
        account_services.validate_update_profile(profile)
        account = account_services.update_profile(sub=payload.get('sub'), profile=profile, session=session)
        return Response(account_schema.dump(account), status=200)
    except Exception as err:
        raise err
