from sqlalchemy import Column, Integer, String, DATETIME
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship

from app import Base


class Calendar(Base):
    __tablename__ = 'calendars'
    id = Column(Integer, primary_key=True)
    platform_id = Column(String)
    type = Column(String)
    description = Column(String)
    location = Column(String)
    summary = Column(String)
    timezone = Column(String)
    background_color = Column(String)
    color_id = Column(String)
    default_reminders = Column(ARRAY(JSONB))
    foreground_color = Column(String)
    notification_settings = Column(JSONB)
    created_by = Column(JSONB)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

    events = relationship('Event', back_populates='calendars')
    association_events = relationship('CalendarEvent', back_populates='calendars', cascade='all, delete-orphan')
    association_connections = relationship('ConnectionCalendar',
                                           back_populates='calendars', cascade='all, delete-orphan')

    def update(self, other):
        if other.description:
            self.description = other.description
        if other.location:
            self.location = other.location
        if other.summary:
            self.summary = other.summary
        if other.timezone:
            self.timezone = other.timezone
        if other.background_color:
            self.background_color = other.background_color
        if other.color_id:
            self.color_id = other.color_id
        if other.default_reminders:
            self.default_reminders = other.default_reminders
        if other.foreground_color:
            self.foreground_color = other.foreground_color
        if other.notification_settings:
            self.notification_settings = other.notification_settings
        if other.created_by:
            self.created_by = other.created_by
