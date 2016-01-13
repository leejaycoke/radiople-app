# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields

from radiople.console.response.common import PagingResponse

from radiople.console.response.audio import Audio


class EpisodeScoreboard(Schema):

    episode_id = fields.Integer()
    like_count = fields.Integer()
    play_count = fields.Integer()


class Episode(Schema):

    id = fields.Integer()
    broadcast_id = fields.Integer()
    title = fields.String(default=None)
    subtitle = fields.String(default=None)
    audio_id = fields.Integer()
    description = fields.String(default=None)
    air_date = fields.LocalDateTime()
    audio = fields.Nested(Audio)
    guest = fields.List(fields.String())


class EpisodeResponse(Episode):

    pass


class EpisodeListResponse(PagingResponse):

    item = fields.Nested(EpisodeResponse, many=True)
