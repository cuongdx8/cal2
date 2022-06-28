import os
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])


def transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            session.begin()
            try:
                result = func(*args, **kwargs, session=session)
            except Exception as err:
                session.rollback()
                raise err
            else:
                session.commit()
        return result

    return wrapper


def connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs, session=Session(engine))
        return result
    return wrapper
