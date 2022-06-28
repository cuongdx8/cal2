from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.account.account import Account


def is_username_or_email_existing(username: str, email: str, session: Session) -> bool:
    # result = session.query(Account).filter(((Account.username == username, Account.active_flag == True) | (Account.email == email))).count()
    sql = f"select count(1) from account where (email = '{email}' and active_flag = true) or username = '{username}'"
    result = session.execute(sql).scalar()
    return True if result > 0 else False
