from marshmallow import Schema
from marshmallow import fields


class Paging(Schema):

    total_count = fields.Integer()
    next = fields.String(default=None)


class PagingResponse(Schema):

    paging = fields.Nested(Paging)
