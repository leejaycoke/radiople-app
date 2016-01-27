# -*- coding: utf-8 -*-

from radiople.db import Session

from radiople.service import Service

from radiople.model.storage import Storage


class StorageService(Service):

    __model__ = Storage

    def get_by_filename(self, filename):
        return Session.query(self.__model__) \
            .filter(Storage.filename == filename).scalar()


class ConsoleStorageService(StorageService):
    pass


service = StorageService()
