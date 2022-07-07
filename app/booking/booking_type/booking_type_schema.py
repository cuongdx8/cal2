from marshmallow import Schema, fields, post_load

from app.booking.booking_type.booking_type import BookingType


class BookingTypeSchema(Schema):
    id = fields.Integer()
    account_id = fields.Integer()
    availability_id = fields.Integer()
    title = fields.String()
    url = fields.String()
    description = fields.String()
    duration = fields.Integer()
    locations = fields.Dict()
    event_name = fields.String()
    additional_inputs = fields.Dict()
    private_url = fields.String()
    minimum_booking_notice = fields.Integer()
    time_slot_intervals = fields.Integer()
    invitees_can_schedule = fields.Dict()
    buffer_time = fields.Dict()
    offer_seats_number = fields.Integer()
    redirect_url = fields.String()

    offer_seats_flag = fields.Boolean()
    private_url_flag = fields.Boolean()
    required_confirm_flag = fields.Boolean()
    recurrence_flag = fields.Boolean()
    disable_guests_flag = fields.Boolean()
    hide_in_calendar_flag = fields.Boolean()
    hide_flag = fields.Boolean()

    @post_load
    def make_booking_type(self, data, **kwargs):
        return BookingType(**data)
