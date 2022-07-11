from sqlalchemy.orm import Session


def is_username_or_email_existing(username: str, email: str, session: Session) -> bool:
    sql = f"select count(1) from account where (email = '{email}' and active_flag = true) or username = '{username}'"
    result = session.execute(sql).scalar()
    return True if result > 0 else False
