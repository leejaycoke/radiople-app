# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Category(Schema):

    id = fields.Integer()
    name = fields.String()


class CategoriesResponse(Schema):

    categories = fields.Nested(Category, many=True)
