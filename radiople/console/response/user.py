from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse


class User(Schema):

    id = fields.Integer()
    nickname = fields.String()


class UserListResponse(PagingResponse):

    item = fields.Nested(User, many=True)
