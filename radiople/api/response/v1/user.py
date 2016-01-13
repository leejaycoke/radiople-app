from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse


class User(Schema):

    id = fields.Integer()
    nickname = fields.String()
    profile_image = fields.Url()
    cover_image = fields.Url()


class UserResponse(User):
    pass


class UserPrivateResponse(User):

    created_at = fields.LocalDateTime()
    email = fields.Email()
    is_verified = fields.Boolean(default=False)


class UserRegisterResponse(Schema):

    user_id = fields.Integer()
    access_token = fields.String()


class UserListResponse(PagingResponse):

    item = fields.Nested(User, many=True)
