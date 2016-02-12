# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.broadcast import Broadcast
from radiople.model.sb_broadcast import SbBroadcast
from radiople.model.subscription import Subscription

from sqlalchemy import func
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import tuple_

from sqlalchemy.orm import joinedload


class BroadcastService(Service):

    __model__ = Broadcast

    def exists(self, broadcast_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(Broadcast.id == broadcast_id).exists()
        ).scalar()

    def get_by_title(self, title):
        return Session.query(self.__model__) \
            .filter(Broadcast.title == title).scalar()

    def exists_title(self, title):
        return Session.query(
            Session.query(self.__model__)
            .filter(Broadcast.title == title).exists()
        ).scalar()

    def get_all(self):
        return Session.query(Broadcast) \
            .filter(Broadcast.id >= 129) \
            .order_by(asc(Broadcast.id)).all()

    def get_by_feed_url(self, feed_url):
        return Session.query(self.__model__) \
            .filter(Broadcast.extra.contains({'feed_url': feed_url})) \
            .scalar()

    def is_subscriber_scalar(self, user_id, broadcast_id):
        return Session.query(self.__model__) \
            .filter(Subscription.broadcast_id == self.broadcast_id) \
            .filter(Subscription.user_id == user_id).as_scalar()


class ApiBroadcastService(BroadcastService):

    def get_ranking_list(self, paging):
        query = Session.query(self.__model__) \
            .options(joinedload('*', innerjoin=True))

        total_count = query.with_entities(func.count(Broadcast.id)).scalar()

        if paging.cursor:
            query = query.filter(
                tuple_(SbBroadcast.score, Broadcast.id) <= paging.cursor)

        item = query.join(SbBroadcast) \
            .order_by(desc(SbBroadcast.score), desc(Broadcast.id)) \
            .limit(paging.limit + 1).all()

        if len(item) > paging.limit:
            cursor = item[-1].scoreboard.score, item[-1].id
        else:
            cursor = None

        return item[:paging.limit], total_count, cursor

    def get_list_by_category_id(self, category_id, paging):
        query = Session.query(self.__model__) \
            .options(joinedload('*', innerjoin=True)) \
            .filter(Broadcast.category_id == category_id)

        total_count = query.with_entities(func.count(Broadcast.id)).scalar()

        by = paging.get_by(['score', 'latest_air_date']) or 'score'

        if paging.cursor:
            query = query.filter(tuple_(paging.cursor) <= paging.cursor)

        query = query.join(SbBroadcast)

        if by == 'score':
            query = query.order_by(desc(SbBroadcast.score), desc(Broadcast.id))
        else:  # latest_air_date
            query = query.order_by(
                desc(Broadcast.latest_air_date), desc(Broadcast.id))

        item = query.limit(paging.limit + 1).all()

        if len(item) > paging.limit:
            if by == 'score':
                cursor = item[-1].scoreboard.score, item[-1].id
            else:  # latest_air_date
                cursor = item[-1].latest_air_date, item[-1].id
        else:
            cursor = None

        return item[:paging.limit], total_count, cursor

    def get_list_by_search(self, paging):
        query = Session.query(self.__model__) \
            .options(joinedload('*', innerjoin=True)) \
            .filter(Broadcast.title.like('%' + paging.q + '%'))

        total_count = query.with_entities(func.count(Broadcast.id)).scalar()

        if paging.cursor:
            query = query.filter(tuple_(paging.cursor) <= paging.cursor)

        item = query.join(SbBroadcast) \
            .order_by(desc(SbBroadcast.score)) \
            .limit(paging.limit + 1).all()

        if len(item) > paging.limit:
            cursor = item[-1].scoreboard.score, item[-1].id
        else:
            cursor = None

        return item[:paging.limit], total_count, cursor

    def get_list(self, paging):
        pass


class ConsoleBroadcastService(BroadcastService):

    def get_all_by_user_id(self, user_id):
        return Session.query(self.__model__) \
            .filter(Broadcast.user_id == user_id) \
            .options(joinedload('*')) \
            .order_by(desc(Broadcast.id)).all()


service = BroadcastService()
api_service = ApiBroadcastService()
console_service = ConsoleBroadcastService()
