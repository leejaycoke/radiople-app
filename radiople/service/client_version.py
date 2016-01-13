# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.client_version import ClientVersion

from sqlalchemy import desc


class ClientVersionService(Service):

    __model__ = ClientVersion

    pass


class ApiClientVersionService(ClientVersionService):

    def get(self, os, app_version):
        query = Session.query(self.__model__) \
            .filter(ClientVersion.os == os) \
            .filter(ClientVersion.app_version > app_version) \
            .filter(ClientVersion.is_active == True)

        is_force = Session.query(
            query.filter(ClientVersion.is_force == True).exists()
        ).as_scalar()

        item = query.add_columns(is_force.label('is_force')) \
            .order_by(desc(ClientVersion.app_version)).first()

        if item:
            item.ClientVersion.is_force = item.is_force
            return item.ClientVersion

service = ClientVersionService()
api_service = ApiClientVersionService()
