from marshmallow import Schema, fields, post_load

from app.account.profile.profile import Profile


class ProfileSchema(Schema):
    id = fields.Integer()
    account_id = fields.Integer()
    full_name = fields.String()
    avatar = fields.String()
    description = fields.String()
    language = fields.String(missing='en')
    timezone = fields.String(missing='UTC')
    time_format = fields.String(missing='HH')
    first_day_of_week = fields.String(missing='su')

    @post_load
    def make_profile(self, data, **kwargs):
        return Profile(**data)