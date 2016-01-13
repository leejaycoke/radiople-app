# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Theme(Schema):

    id = fields.Integer()
    title = fields.String()
