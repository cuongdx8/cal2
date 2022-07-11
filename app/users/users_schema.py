from marshmallow import Schema, fields, post_load

from app.users.users import User
from app.users.profiles.profiles_schema import ProfileSchema


class UserSchema(Schema):
    id = fields.Integer()
    platform_id = fields.Integer()
    type = fields.String()
    credentials = fields.Dict()
    username = fields.String()
    email = fields.String()
    password = fields.String()
    active_flag = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    profile = fields.Nested(ProfileSchema)

    @post_load
    def make_account(self, data, **kwargs):
        return User(**data)
