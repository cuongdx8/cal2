from app.account.account_schema import AccountSchema
from app.booking.availability.availability_schema import AvailabilitySchema
from app.booking.booking_schema import BookingSchema
from app.booking.booking_type.booking_type_schema import BookingTypeSchema
from app.calendar.calendar_schema import CalendarSchema
from app.event.event_schema import EventSchema

account_schema = AccountSchema()
calendar_schema = CalendarSchema()
event_schema = EventSchema()
booking_availability_schema = AvailabilitySchema()
booking_type_schema = BookingTypeSchema()
booking_schema = BookingSchema()
