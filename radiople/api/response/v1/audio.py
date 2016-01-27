# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Audio(Schema):

    filename = fields.String()
    display_length = fields.String()
    display_size = fields.String()
    length = fields.Integer()
    url = fields.Url()
