# -*- coding: utf-8 -*-

from radiople.service import Service

from radiople.model.storage_log import StorageLog


class StorageLogService(Service):

    __model__ = StorageLog


class ApiStorageLogService(StorageLogService):

    pass


service = StorageLogService()
api_service = ApiStorageLogService()
