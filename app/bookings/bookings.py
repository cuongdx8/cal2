from sqlalchemy import Column, Integer, ForeignKey, String, DATETIME, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from app import Base


class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('users.id'))
    booking_type_id = Column(Integer, ForeignKey('booking_types.id'))
    partner_name = Column(String)
    event_name = Column(String)
    guests = Column(ARRAY(String))
    locations = Column(JSONB)
    additional_notes = Column(JSONB)
    start = Column(DATETIME)
    end = Column(DATETIME)
    recurrence = Column(String)
    confirm_flag = Column(Boolean)
    cancelled_flag = Column(Boolean)

    def update(self, other):
        if other.id:
            self.id = other.id
        if other.account_id:
            self.account_id = other.account_id
        if other.booking_type_id:
            self.booking_type_id = other.booking_type_id
        if other.partner_name:
            self.partner_name = other.partner_name
        if other.event_name:
            self.event_name = other.event_name
        if other.guests:
            self.guests = other.guests
        if other.locations:
            self.locations = other.locations
        if other.additional_notes:
            self.additional_notes = other.additional_notes
        if other.start:
            self.start = other.start
        if other.end:
            self.end = other.end
        if other.recurrence:
            self.recurrence = other.recurrence
        if other.confirm_flag:
            self.confirm_flag = other.confirm_flag
        if other.cancelled_flag:
            self.cancelled_flag = other.cancelled_flag
