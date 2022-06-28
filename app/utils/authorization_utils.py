import logging
import traceback
from functools import wraps

from flask import request, Response
from app.exception import JWTError
from app.utils import jwt_utils


def verify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            try:
                payload = jwt_utils.get_payload(request.headers['Authorization'][7:])
                result = func(*args, payload=payload, **kwargs)
                return result
            except JWTError:
                logging.getLogger().error(traceback.print_exc())
                return Response("'Invalid JWT', 'User does not exist'", status=401)
            except Exception as err:
                raise err
        else:
            return Response("'Authorization Required', 'Request does not contain an access token'", status=401)

    return wrapper


def unverify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as err:
            raise err
    return wrapper
