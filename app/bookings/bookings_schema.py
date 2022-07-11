from marshmallow import Schema, fields, post_load

from app.bookings.bookings import Booking


class BookingSchema(Schema):
    id = fields.Integer()
    account_id = fields.Integer()
    booking_type = fields.Integer()
    partner_name = fields.String()
    name = fields.String()
    guests = fields.List(fields.String())
    locations = fields.Dict()
    additional_notes = fields.Dict()
    start = fields.DateTime()
    end = fields.DateTime()
    recurrence = fields.String()
    is_confirm = fields.Boolean()
    is_cancelled = fields.Boolean()

    @post_load
    def make_booking(self, data, **kwargs):
        return Booking(**data)
