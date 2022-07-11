from flask import Blueprint, Response, request
from requests import Session

from app.users import users_services
from app.schemas import user_schema, profile_schema
from app.utils.authorization_utils import verify
from app.utils.database_utils import connection, transaction

bp_user = Blueprint('users', __name__, url_prefix='/users')


@bp_user.route('/me', methods=['GET'])
@verify
@connection
def me(payload: dict, session: Session):
    try:
        account = users_services.info(sub=payload.get('sub'), session=session)
        return Response(user_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_user.route('/change_password', methods=['POST'])
@verify
@transaction
def change_password(payload, session):
    try:
        data = request.get_json()
        users_services.validate_change_password(old_password=data.get('old_password'),
                                                new_password=data.get('new_password'))
        account = users_services.change_password(sub=payload.get('sub'), old_password=data.get('old_password'),
                                                 new_password=data.get('new_password'), session=session)
        return Response(user_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_user.route('/{username}/profile', methods=['GET'])
@connection
def get_profile(username: str, session: Session):
    try:
        account = users_services.get_profile(username=username, session=session)
        return Response(user_schema.dump(account), status=200)
    except Exception as err:
        raise err


@bp_user.route('/profile', methods=['PATCH'])
@verify
@transaction
def update_profile(payload, session):
    try:
        data = request.get_json()
        # account_services.validate_update_profile()
        profile = profile_schema.load(data)
        users_services.validate_update_profile(profile)
        account = users_services.update_profile(sub=payload.get('sub'), profile=profile, session=session)
        return Response(user_schema.dump(account), status=200)
    except Exception as err:
        raise err
