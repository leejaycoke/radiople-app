# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.v1.theme import Theme
from radiople.api.response.v1.broadcast import Broadcast


class ThemeBroadcasts(Schema):

    theme = fields.Nested(Theme)
    broadcasts = fields.Nested(Broadcast, many=True)


class NewsResponse(Schema):

    theme_broadcasts = fields.Nested(ThemeBroadcasts, many=True)
