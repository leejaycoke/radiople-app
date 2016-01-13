# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.v1.user import User


class ClientVersion(Schema):

    os = fields.String(default=None)
    app_version = fields.String(default=None)
    has_update = fields.Boolean(default=False)
    is_force = fields.Boolean(default=False)


class StaticImage(Schema):

    position = fields.String(default=None)
    image = fields.Url()


class SystemCheckResponse(Schema):

    client_version = fields.Nested(ClientVersion)
    static_images = fields.Nested(StaticImage, many=True)
