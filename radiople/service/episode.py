# -*- coding: utf-8 -*-

from flask import request

from dateutil.parser import parse as parse_date

from radiople.db import Session
from radiople.service import Service

from radiople.model.episode import Episode
from radiople.model.episode_like import EpisodeLike
from radiople.model.history import History

from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class EpisodeService(Service):

    __model__ = Episode

    @property
    def user_properties(self):
        user_id = request.auth.user_id
        return [self.is_like_as_scalar(user_id), self.position_as_scalar(user_id)]

    def is_like_as_scalar(self, user_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(EpisodeLike.episode_id == Episode.id)
            .filter(EpisodeLike.user_id == user_id)
            .correlate(Episode)
            .exists()).as_scalar().label('is_like')

    def position_as_scalar(self, user_id):
        return Session.query(self.__model__) \
            .with_entities(History.position) \
            .filter(History.episode_id == Episode.id) \
            .filter(History.user_id == user_id) \
            .correlate(Episode) \
            .as_scalar().label('position')

    def guess_exists_episode(self, broadcast_id, title, air_date):
        return Session.query(
            Session.query(self.__model__)
            .filter(Episode.broadcast_id == broadcast_id)
            .filter(Episode.title == title)
            .filter(Episode.air_date == air_date).exists()
        ).scalar()

    def exists_title_by_broadcast_id(self, broadcast_id, title):
        return Session.query(
            Session.query(self.__model__)
            .filter(Episode.broadcast_id == broadcast_id)
            .filter(Episode.title == title).exists()
        ).scalar()

    def exists_air_date_by_broadcast_id(self, broadcast_id, air_date):
        return Session.query(
            Session.query(self.__model__)
            .filter(Episode.broadcast_id == broadcast_id)
            .filter(Episode.air_date == air_date).exists()
        ).scalar()

    def get_latest_episode(self, broadcast_id):
        return Session.query(self.__model__) \
            .order_by(desc(Episode.air_date)) \
            .filter(Episode.broadcast_id == broadcast_id).first()


class ApiEpisodeService(EpisodeService):

    def exists(self, episode_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(Episode.id == episode_id).exists()
        ).scalar()

    def get_next(self, episode_id):
        """ episode_id보다 최근 에피소드를 가져온다. """

        episode = self.get(episode_id)
        try:
            return Session.query(self.__model__) \
                .filter(Episode.broadcast_id == episode.broadcast_id) \
                .filter(Episode.air_date > episode.air_date) \
                .order_by(asc(Episode.air_date)).first()
        except:
            return None

    def get_prev(self, episode_id):
        """ episode_id보다 이 전 에피소드를 가져온다. """

        episode = self.get(episode_id)
        try:
            return Session.query(self.__model__) \
                .filter(Episode.broadcast_id == episode.broadcast_id) \
                .filter(Episode.air_date < episode.air_date) \
                .order_by(desc(Episode.air_date)).first()
        except:
            return None

    def get_list(self, broadcast_id, paging):
        query = Session.query(self.__model__) \
            .filter(Episode.broadcast_id == broadcast_id) \
            .options(joinedload('*', innerjoin=True))

        total_count = query.with_entities(
            func.count(Episode.broadcast_id)).scalar()

        if paging.cursor:
            cursor = parse_date(paging.cursor)
            query = query.filter(Episode.air_date <= cursor)

        query = query.order_by(desc(Episode.air_date))

        item = query.limit(paging.limit + 1).all()

        cursor = item[-1].air_date if len(item) > paging.limit else None

        return (item[:paging.limit], total_count, cursor)


class ConsoleEpisodeService(EpisodeService):

    def get_list(self, broadcast_id, paging):
        query = Session.query(self.__model__) \
            .filter(Episode.broadcast_id == broadcast_id)

        if paging.q:
            query = query.filter(Episode.title.like('%' + paging.q + '%'))

        total_count = query.with_entities(func.count(Episode.id)).scalar()

        item = query.options(joinedload('*', innerjoin=True)) \
            .order_by(desc(Episode.air_date)) \
            .limit(paging.page_size) \
            .offset(paging.offset).all()

        return item, total_count

    def get_by_audio_id(self, audio_id):
        return Session.query(self.__model__) \
            .filter(Episode.audio_id == audio_id).scalar()


service = EpisodeService()
api_service = ApiEpisodeService()
console_service = ConsoleEpisodeService()
