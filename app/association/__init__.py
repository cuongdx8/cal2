from sqlalchemy import Table, Column, ForeignKey, String, BOOLEAN, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app import Base

association_account_connection = Table('account_connection', Base.metadata,
                                       Column('account_id', ForeignKey('users.id'), primary_key=True),
                                       Column('connection_id', ForeignKey('connections.id'), primary_key=True)
                                       )


class ConnectionCalendar(Base):
    __tablename__ = 'connection_calendar'
    connection_id = Column(Integer, ForeignKey('connections.id'), primary_key=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'), primary_key=True)
    access_role = Column(String)
    default_flag = Column(BOOLEAN)
    owner_flag = Column(BOOLEAN)
    connection = relationship('Connection', back_populates="association_calendars")
    calendar = relationship('Calendar', back_populates='association_connections')


class CalendarEvent(Base):
    __tablename__ = 'calendar_event'
    calendar_id = Column(Integer, ForeignKey('calendars.id'), primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    overrides = Column(JSONB)
    owner_flag = Column(BOOLEAN)
    response_status = Column(String)

    event = relationship('Event', back_populates='association_calendars')
    calendar = relationship('Calendar', back_populates='association_events')
