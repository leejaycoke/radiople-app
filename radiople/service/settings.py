# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.settings import Settings


class SettingsService(Service):

    __model__ = Settings


class ApiSettingsService(SettingsService):

    pass


service = SettingsService()
api_service = ApiSettingsService()
