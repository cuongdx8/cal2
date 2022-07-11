import datetime

from sqlalchemy.orm import Session

from app.users.users import User


def add(account: User, session: Session):
    account.updated_at = datetime.datetime.utcnow()
    if account.id:
        account.created_at = account.updated_at
        session.merge(account)
    else:
        session.add(account)


def find_by_id(sub: int, session: Session) -> User:
    account = session.query(User).filter(User.id == sub).first()
    return account


def find_by_email(email: str, session: Session, active_flag=True) -> User:
    return session.query(User).filter(User.email == email, User.active_flag == active_flag).first()


def find_by_username(username: str, session: Session, active_flag=True):
    return session.query(User).filter(User.username == username, User.active_flag == active_flag).first()


def find_by_platform_id_and_type(platform_id: str, type: str, session: Session, active_flag=True):
    account = session.query(User).filter(User.platform_id == platform_id,
                                         User.type == type,
                                         User.active_flag == active_flag).first()
    return account


def find_by_email_and_platform(email: str, type: str, session: Session, active_flag=True):
    account = session.query(User).filter(User.email == email,
                                         User.type == type,
                                         User.active_flag == active_flag).first()
    return account
