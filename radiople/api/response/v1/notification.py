# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse


class Notification(Schema):

    id = fields.Integer()
    landing = fields.String()
    extra = fields.Field()
    message = fields.String()
    created_at = fields.LocalDateTime()


class NotificationListResponse(PagingResponse):

    item = fields.Nested(Notification, many=True)
