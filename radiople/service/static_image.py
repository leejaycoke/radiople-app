# -*- coding: utf-8 -*-

from radiople.db import Session

from radiople.service import Service

from radiople.model.static_image import StaticImage


class StaticImageService(Service):

    __model__ = StaticImage

    pass


class ApiStaticImageService(StaticImageService):

    def get_all(self):
        return Session.query(self.__model__).all()


service = StaticImageService()
api_service = ApiStaticImageService()
