# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.console.response.common import PagingResponse

from radiople.console.response.storage import Storage


class EpisodeScoreboard(Schema):

    episode_id = fields.Integer()
    like_count = fields.Integer()
    play_count = fields.Integer()


class Episode(Schema):

    id = fields.Integer()
    broadcast_id = fields.Integer()
    title = fields.String(default=None)
    subtitle = fields.String(default=None)
    storage_id = fields.Integer()
    description = fields.String(default=None)
    air_date = fields.LocalDateTime()
    storage = fields.Nested(Storage)
    guest = fields.List(fields.String())
    scoreboard = fields.Nested(EpisodeScoreboard)


class EpisodeResponse(Episode):

    pass


class EpisodeListResponse(PagingResponse):

    item = fields.Nested(EpisodeResponse, many=True)
