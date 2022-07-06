
from marshmallow import Schema, fields, post_load

from app.event.event import Event


class EventSchema(Schema):
    id = fields.Integer()
    platform_id = fields.String()
    attachments = fields.Dict()
    attendees = fields.Dict()
    description = fields.String()
    color_id = fields.String()
    conference_data = fields.Dict()
    creator = fields.Dict()
    end = fields.Dict()
    end_time_unspecified = fields.Boolean()
    event_type = fields.String()
    extended_properties = fields.Dict()
    guests_can_invite_others = fields.Boolean()
    guests_can_modify = fields.Boolean()
    guests_can_see_other_guests = fields.Boolean()
    html_link = fields.String()
    uid = fields.String()
    location = fields.String()
    locked = fields.Boolean()
    organizer = fields.Dict()
    original_start_time = fields.Dict()
    private_copy = fields.Boolean()
    recurrence = fields.List(fields.String())
    recurring_event_id = fields.String()
    reminders = fields.List(fields.Dict())
    start = fields.Dict()
    status = fields.String()
    summary = fields.String()
    transparency = fields.String()
    updated = fields.DateTime()
    visibility = fields.String()

    @post_load
    def make_event(self, data, **kwargs):
        return Event(**data)