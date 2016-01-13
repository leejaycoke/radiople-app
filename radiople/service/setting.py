# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.setting import Setting


class SettingService(Service):

    __model__ = Setting


class ApiSettingService(SettingService):

    pass


service = SettingService()
api_service = ApiSettingService()
