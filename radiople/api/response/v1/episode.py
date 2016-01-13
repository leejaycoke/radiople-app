# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.api.response.common import PagingResponse

from radiople.api.response.v1.broadcast import Broadcast
from radiople.api.response.v1.audio import Audio
from radiople.api.response.v1.history import History


class EpisodeScoreboard(Schema):

    episode_id = fields.Integer()
    like_count = fields.Integer()
    play_count = fields.Integer()


class EpisodeActivity(Schema):

    is_like = fields.Boolean(default=False)
    position = fields.Integer(default=0)


class Episode(Schema):

    id = fields.Integer()
    broadcast_id = fields.Integer()
    title = fields.String(default=None)
    subtitle = fields.String(default=None)
    content = fields.String(default=None)
    air_date = fields.LocalDateTime()
    broadcast = fields.Nested(Broadcast)
    audio = fields.Nested(Audio)
    scoreboard = fields.Nested(EpisodeScoreboard)
    activity = fields.Nested(EpisodeActivity)


class EpisodeResponse(Episode):

    pass


class EpisodeListResponse(PagingResponse):

    item = fields.Nested(Episode, many=True)
