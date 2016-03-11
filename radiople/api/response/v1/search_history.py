# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse


class SearchHistory(Schema):

    keyword = fields.String()
    updated_at = fields.LocalDateTime()


class SearchHistoryListResponse(PagingResponse):

    item = fields.Nested(SearchHistory, many=True)
    keyword = fields.String()
