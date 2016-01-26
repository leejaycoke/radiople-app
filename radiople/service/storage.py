# -*- coding: utf-8 -*-

from radiople.service import Service

from radiople.model.storage import Storage


class StorageService(Service):

    __model__ = Storage


class ConsoleStorageService(StorageService):
    pass


service = StorageService()
