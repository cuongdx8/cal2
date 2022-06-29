import datetime

from sqlalchemy.orm import Session

from app.connection.connection import Connection


def add(connection: Connection, session: Session):
    connection.updated_at = datetime.datetime.utcnow()
    if connection.id:
        session.merge(connection)
    else:
        connection.created_at = connection.updated_at
        session.add(connection)