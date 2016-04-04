# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Settings(Schema):

    is_user_push_active = fields.Boolean(default=False)
    is_ad_push_active = fields.Boolean(default=False)
    is_subscription_push_active = fields.Boolean(default=False)
    is_mobile_network_active = fields.Boolean(default=False)
    skip_seconds = fields.Integer(default=30)
    player_finish_activity = fields.String(default="stop")


class SettingsResponse(Settings):

    pass
