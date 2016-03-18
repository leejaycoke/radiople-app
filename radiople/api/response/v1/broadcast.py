# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse
from radiople.api.response.v1.category import Category


class BroadcastScoreboard(Schema):

    episode_count = fields.Integer()
    comment_count = fields.Integer()
    subscription_count = fields.Integer()
    rating_count = fields.Integer()
    rating_average = fields.Float()


class BroadcastActivity(Schema):

    is_subscriber = fields.Boolean()
    rating_point = fields.Float()


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
    scoreboard = fields.Nested(BroadcastScoreboard)
    activity = fields.Nested(BroadcastActivity)


class BroadcastResponse(Broadcast):
    pass


class BroadcastListResponse(PagingResponse):

    item = fields.Nested(Broadcast, many=True)
