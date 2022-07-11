from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app import Base


class Availability(Base):
    __tablename__ = 'availabilitys'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    account_id = Column(Integer, ForeignKey('users.id'))
    availability_by_week_days = Column(JSONB)
    timezone = Column(String)
    default_flag = Column(Boolean, default=False)

    def update(self, other):
        if other.event_name:
            self.name = other.event_name
        if other.account_id:
            self.account_id = other.account_id
        if other.availability_by_week_days:
            self.availability_by_week_days = other.availability_by_week_days
        if other.timezone:
            self.timezone = other.timezone
        if other.default_flag:
            self.default_flag = other.default_flag
