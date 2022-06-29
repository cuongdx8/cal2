from sqlalchemy import Column, Integer, ForeignKey, String

from app import Base


class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    full_name = Column(String)
    avatar = Column(String)
    description = Column(String)
    language = Column(String)
    timezone = Column(String)
    time_format = Column(String)
    first_day_of_week = Column(String)

    def update(self, other):
        if other.full_name:
            self.full_name = other.full_name
        if other.avatar:
            self.avatar = other.avatar
        if other.description:
            self.description = other.description
        if other.language:
            self.language = other.language
        if other.timezone:
            self.timezone = other.timezone
        if other.time_format:
            self.time_format = other.time_format
        if other.first_day_of_week:
            self.first_day_of_week = other.first_day_of_week
