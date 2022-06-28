import os
from datetime import datetime, timedelta

import jwt
import codecs

from app.account.account_schema import AccountSchema
from app.constants import Constants
from app.exception import JWTError

algorithm = os.environ['JWT_ALGORITHM']
jwt_key = os.environ['JWT_SECRET_KEY']


def create_access_token(account):
    data = {
        'iss': Constants.APP_HOST,
        'iat': datetime.now(),
        'exp': datetime.now() + timedelta(days=Constants.EXPIRED_DAY_NUMBER),
        'sub': str(account.id)
    }
    return jwt.encode(data, algorithm=algorithm, key=jwt_key)


def create_forgot_token(account):
    data = {
        'exp': datetime.now() + timedelta(hours=Constants.EXPIRED_HOURS_NUMBER),
        'sub': str(account.id)
    }
    return codecs.decode(jwt.encode(data, algorithm=algorithm, key=jwt_key), 'UTF-8')


def get_payload(token):
    try:
        result = jwt.decode(token, algorithms=algorithm, key=jwt_key)
        return result
    except:
        raise JWTError()


def create_invite_token(event_id, item):
    data = {
        'exp': datetime.now() + timedelta(hours=Constants.EXPIRED_HOURS_NUMBER),
        'sub': str(item.get('email')),
        'event_id': str(event_id)
    }
    return jwt.encode(data, algorithm=algorithm, key=jwt_key)


def create_active_token(id):
    data = {
        'exp': datetime.now() + timedelta(hours=Constants.EXPIRED_HOURS_NUMBER),
        'sub': str(id),
    }
    return jwt.encode(data, algorithm=algorithm, key=jwt_key)
