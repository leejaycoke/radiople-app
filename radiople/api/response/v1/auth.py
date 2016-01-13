from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.v1.user import UserPrivateResponse


class Session(Schema):

    access_token = fields.String()
    expires_at = fields.LocalDateTime()


class UserSessionResponse(Schema):

    user = fields.Nested(UserPrivateResponse)
    session = fields.Nested(Session)
