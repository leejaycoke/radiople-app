# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Audio(Schema):

    id = fields.Integer()
    url = fields.Url()
