# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Topic(Schema):

    names = fields.List(fields.String)


class TopicResponse(Topic):
    pass
