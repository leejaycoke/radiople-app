# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Storage(Schema):

    filename = fields.String()
    extra = fields.Field()
    mimes = fields.List(fields.String())
    url = fields.Url()
    file_type = fields.String()
