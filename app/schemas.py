from app.users.profiles.profiles_schema import ProfileSchema
from app.users.users_schema import UserSchema
from app.bookings.availabilitys.availability_schema import AvailabilitySchema
from app.bookings.bookings_schema import BookingSchema
from app.bookings.booking_types.booking_types_schema import BookingTypeSchema
from app.calendars.calendars_schema import CalendarSchema
from app.events.events_schema import EventSchema

users_schema = UserSchema()
calendars_schema = CalendarSchema()
events_schema = EventSchema()
booking_availability_schema = AvailabilitySchema()
booking_type_schema = BookingTypeSchema()
bookings_schema = BookingSchema()
profiles_schema = ProfileSchema()
