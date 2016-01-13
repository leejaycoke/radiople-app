# -*- coding: utf-8 -*-

from radiople.service import Service


from radiople.model.rating import Rating


class RatingService(Service):

    __model__ = Rating


class ApiRatingService(RatingService):

    pass


api_service = ApiRatingService()
