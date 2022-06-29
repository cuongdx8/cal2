from sqlalchemy import Table, Column, ForeignKey, String, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app import Base

association_account_connection = Table('account_connection', Base.metadata,
                                       Column('account_id', ForeignKey('account.id'), primary_key=True),
                                       Column('connection_id', ForeignKey('connection.id'), primary_key=True)
                                       )


class ConnectionCalendar(Base):
    __tablename__ = 'connection_calendar'
    connection_id = Column(UUID(as_uuid=True), ForeignKey('connection.id'), primary_key=True)
    calendar_id = Column(UUID(as_uuid=True), ForeignKey('calendar.id'), primary_key=True)
    access_role = Column(String)
    default_flag = Column(BOOLEAN)
    connection = relationship('Connection', back_populates="association_calendars")
    calendar = relationship('Calendar', back_populates='association_connections')
