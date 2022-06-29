from marshmallow import Schema, fields, post_load

from app.account.account import Account
from app.account.profile.profile_schema import ProfileSchema


class AccountSchema(Schema):
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
        return Account(**data)