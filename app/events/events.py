from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DATETIME
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship

from app import Base


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'))
    platform_id = Column(String)
    type = Column(String)
    attachments = Column(ARRAY(JSONB))
    attendees = Column(ARRAY(JSONB))
    description = Column(String)
    color_id = Column(String)
    conference_data = Column(JSONB)
    creator = Column(JSONB)
    end = Column(JSONB)
    end_time_unspecified = Column(Boolean)
    event_type = Column(String)
    extended_properties = Column(JSONB)
    guests_can_invite_others = Column(Boolean)
    guests_can_modify = Column(Boolean)
    guests_can_see_other_guests = Column(Boolean)
    html_link = Column(String)
    uid = Column(String)
    location = Column(String)
    locked = Column(Boolean)
    organizer = Column(JSONB)
    original_start_time = Column(JSONB)
    private_copy = Column(Boolean)
    recurrence = Column(ARRAY(String))
    recurring_event_id = Column(String)
    reminders = Column(ARRAY(JSONB))
    start = Column(JSONB)
    status = Column(String)
    summary = Column(String)
    transparency = Column(String)
    updated = Column(DATETIME)
    visibility = Column(String)

    association_calendars = relationship('CalendarEvent', back_populates='events')
    calendar = relationship('Calendar', back_populates='events')
