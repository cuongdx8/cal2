from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow.fields import Dict

from app.calendar.calendar import Calendar


class CalendarSchema(Schema):
    id = fields.Integer()
    platform_id = fields.String()
    type = fields.String()
    description = fields.String()
    location = fields.String()
    summary = fields.String()
    timezone = fields.String()
    background_color = fields.String()
    color_id = fields.String()
    default_reminders = fields.List(Dict())
    foreground_color = fields.String()
    notification_settings = Dict()
    created_by = Dict()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @post_load
    def make_calendar(self, data, **kwargs):
        calendar = Calendar(**data)
        return calendar

    class Meta:
        unknown = EXCLUDE
