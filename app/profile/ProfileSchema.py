from marshmallow import Schema, fields


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
