# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.console.response.category import Category


class BroadcastScoreboard(Schema):

    episode_count = fields.Integer()
    comment_count = fields.Integer()
    subscriber_count = fields.Integer()
    rating_count = fields.Integer()
    rating_average = fields.Float()


class Broadcast(Schema):

    id = fields.Integer()
    title = fields.String()
    subtitle = fields.String(default=None)
    casting = fields.List(fields.String())
    icon_image = fields.Url()
    cover_image = fields.Url()
    latest_air_date = fields.LocalDateTime()
    start_at = fields.Date()
    notice = fields.String(default=None)
    description = fields.String(default=None)
    category = fields.Nested(Category)
    category_id = fields.Integer()
    link = fields.Url()
    scoreboard = fields.Nested(BroadcastScoreboard)


class BroadcastResponse(Broadcast):

    pass


class BroadcastsResponse(Schema):

    broadcasts = fields.Nested(Broadcast, many=True)
