# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


GCM_PER_SIZE = 1000


class Landing(object):

    BROADCAST = 'broadcast'
    SUBSCRIPTION = 'subscription'
    MAIN = 'main'
    CATEGORY = 'category'


class PushBuilder(object):

    param = {}
    extra = {}

    def __init__(self, landing):
        self.landing = landing
        self.extra_serializer = self.extra_serializers.get(landing)

    def build(self):
        self.param['extra'] = self.extra_serializer(self.extra).data
        payload = PushSchema(self.param).data
        return payload

    def add_param(self, **kwargs):
        self.param.update(kwargs)
        return self

    def add_extra(self, **kwargs):
        self.extra.update(kwargs)
        return self

    @property
    def extra_serializers(self):
        return {
            Landing.BROADCAST: BroadcastSchema,
            Landing.MAIN: MainSchema,
            Landing.CATEGORY: CategorySchema,
        }


class PushSchema(Schema):

    title = fields.String()
    message = fields.String()
    icon_image = fields.Url()
    cover_image = fields.Url()

    extra = fields.Field()


class MainSchema(Schema):

    class Position(object):

        NEWS = 'news'
        RANKING = 'ranking'
        CATEGORY = 'category'

    position = fields.String()


class BroadcastSchema(Schema):

    class Broadcast(Schema):
        id = fields.Integer()
        title = fields.String()
        casting = fields.List(fields.String())
        icon_image = fields.Url()
        cover_image = fields.Url()
        latest_air_date = fields.LocalDateTime()

    broadcast = fields.Nested(Broadcast)


class CategorySchema(Schema):

    category_id = fields.Integer()


class Subscription(Schema):
    pass
