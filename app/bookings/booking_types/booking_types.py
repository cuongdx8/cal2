from sqlalchemy import Integer, Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from app import Base


class BookingType(Base):
    __tablename__ = 'booking_types'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('users.id'))
    availability_id = Column(Integer, ForeignKey('availabilitys.id'))
    title = Column(String)
    url = Column(String)
    description = Column(String)
    duration = Column(Integer)
    locations = Column(JSONB)
    event_name = Column(String, default='Meeting with {host}')
    additional_inputs = Column(JSONB)
    private_url = Column(String)
    minimum_booking_notice = Column(Integer)
    time_slot_intervals = Column(Integer)
    invitees_can_schedule = Column(JSONB)
    buffer_time = Column(JSONB)
    offer_seats_number = Column(Integer)
    redirect_url = Column(String)
    offer_seats_flag = Column(Boolean)
    private_url_flag = Column(Boolean)
    required_confirm_flag = Column(Boolean)
    recurrence_flag = Column(Boolean)
    disable_guests_flag = Column(Boolean)
    hide_flag = Column(Boolean, default=False)
    hide_in_calendar_flag = Column(Boolean, default=False)

    def update(self, other):
        if other.id:
            self.id = other.id
        if other.account_id:
            self.account_id = other.account_id
        if other.title:
            self.title = other.title
        if other.url:
            self.url = other.url
        if other.description:
            self.description = other.description
        if other.duration:
            self.duration = other.duration
        if other.locations:
            self.locations = other.locations
        if other.event_name:
            self.event_name = other.event_name
        if other.additional_inputs:
            self.additional_inputs = other.additional_inputs
        if other.private_url:
            self.private_url = other.private_url
        if other.minimum_booking_notice:
            self.minimum_booking_notice = other.minimum_booking_notice
        if other.time_slot_intervals:
            self.time_slot_intervals = other.time_slot_intervals
        if other.invitees_can_schedule:
            self.invitees_can_schedule = other.invitees_can_schedule
        if other.buffer_time:
            self.buffer_time = other.buffer_time
        if other.offer_seats_number:
            self.offer_seats_number = other.offer_seats_number
        if other.redirect_url:
            self.redirect_url = other.redirect_url
        if other.offer_seats_flag:
            self.offer_seats_flag = other.offer_seats_flag
        if other.private_url_flag:
            self.private_url_flag = other.private_url_flag
        if other.required_confirm_flag:
            self.required_confirm_flag = other.required_confirm_flag
        if other.recurrence_flag:
            self.recurrence_flag = other.recurrence_flag
        if other.disable_guests_flag:
            self.disable_guests_flag = other.disable_guests_flag
        if other.hide_flag:
            self.hide_flag = other.hide_flag
        if other.hide_in_calendar_flag:
            self.hide_in_calendar_flag = other.hide_in_calendar_flag
