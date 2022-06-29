from sqlalchemy import Column, Integer, String, DATETIME
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app import Base
from app.association import association_account_connection


class Connection(Base):
    __tablename__ = 'connection'
    id = Column(Integer, primary_key=True)
    platform_id = Column(String)
    type = Column(String)
    username = Column(String)
    email = Column(String)
    credentials = Column(JSONB)
    settings = Column(JSONB)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)
    sync_token = Column(String)

    accounts = relationship('Account', secondary=association_account_connection,
                            back_populates='connections')
    association_calendars = relationship('ConnectionCalendar',
                                         back_populates='connection', cascade='all')
