# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import fields


class Setting(Schema):

    user_push = fields.Boolean(default=False)
    all_push = fields.Boolean(default=False)
    subscription_push = fields.Boolean(default=False)


class SettingResponse(Setting):

    pass
