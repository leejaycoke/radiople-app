# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse
from radiople.api.response.v1.user import User


class Comment(Schema):

    id = fields.Integer()
    content = fields.String()
    created_at = fields.LocalDateTime()
    user = fields.Nested(User)
    is_deletable = fields.Boolean()


class CommentResponse(Comment):
    pass


class CommentListResponse(PagingResponse):

    item = fields.Nested(Comment, many=True)
