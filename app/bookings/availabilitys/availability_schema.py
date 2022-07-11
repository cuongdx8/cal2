from marshmallow import Schema, fields, post_load

from app.bookings.availabilitys.availability import Availability


class AvailabilitySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    account_id = fields.Integer()
    availability_by_week_days = fields.Dict()
    timezone = fields.String()
    default_flag = fields.Boolean()

    @post_load
    def make_availability(self, data, **kwargs):
        return Availability(**data)