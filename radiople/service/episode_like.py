# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople import service
from radiople.service import Service

from radiople.model.episode_like import EpisodeLike

from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class EpisodeLikeService(Service):

    __model__ = EpisodeLike


class ApiEpisodeLikeService(EpisodeLikeService):

    def exists(self, episode_id, user_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(EpisodeLike.episode_id == episode_id)
            .filter(EpisodeLike.user_id == user_id).exists()
        ).scalar()


class PartnerEpisodeLikeService(EpisodeLikeService):

    pass


api_service = ApiEpisodeLikeService()
partner_service = PartnerEpisodeLikeService()
