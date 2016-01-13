from marshmallow import Schema
from marshmallow import fields


class Paging(Schema):

    total_count = fields.Integer()
    page = fields.Integer()


class PagingResponse(Schema):

    paging = fields.Nested(Paging)
