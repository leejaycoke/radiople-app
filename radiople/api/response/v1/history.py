# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse
from radiople.api.response.v1.episode import Episode


class History(Schema):

    position = fields.Integer()
    updated_at = fields.LocalDateTime()
    episode = fields.Nested(Episode)


class HistoryResponse(Schema):

    pass


class HistoryListResponse(PagingResponse):

    item = fields.Nested(History, many=True)
