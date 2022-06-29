import datetime

from sqlalchemy.orm import Session

from app.account.account import Account


def add(account: Account, session: Session):
    account.updated_at = datetime.datetime.utcnow()
    if account.id:
        account.created_at = account.updated_at
        session.merge(account)
    else:
        session.add(account)


def find_by_id(sub: str, session: Session) -> Account:
    account = session.query(Account).filter(Account.id == sub).first()
    return account


def find_by_email(email: str, session: Session, active_flag=True) -> Account:
    return session.query(Account).filter(Account.email == email, Account.active_flag == active_flag).first()


def find_by_username(username: str, session: Session, active_flag=True):
    return session.query(Account).filter(Account.username == username, Account.active_flag == active_flag).first()


def find_by_platform_id_and_type(platform_id: str, type: str, session: Session, active_flag=True):
    account = session.query(Account).filter(Account.platform_id == platform_id,
                                            Account.type == type,
                                            Account.active_flag == active_flag).first()
    return account


def find_by_email_and_platform(email: str, type: str, session: Session, active_flag=True):
    account = session.query(Account).filter(Account.email == email,
                                            Account.type == type,
                                            Account.active_flag == active_flag).first()
    return account
