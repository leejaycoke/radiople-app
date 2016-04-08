# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.opensource import OpenSource

from sqlalchemy import asc
from sqlalchemy import desc


class OpenSourceService(Service):

    __model__ = OpenSource

    def get_by_os_app_version(self, os, app_version):
        return Session.query(self.__model__) \
            .filter(OpenSource.os == os) \
            .filter(OpenSource.is_active) \
            .filter(OpenSource.app_version <= app_version) \
            .order_by(desc(OpenSource.app_version)).first()


class ApiOpenSourceService(OpenSourceService):
    pass


class ConsoleOpenSourceService(OpenSourceService):
    pass


service = OpenSourceService()
api_service = ApiOpenSourceService()
console_service = ConsoleOpenSourceService()
