# -*- coding: utf-8 -*-

from radiople.db import Session


from radiople.service import Service

from radiople.api.common import make_paging

from radiople.model.broadcast import Broadcast
from radiople.model.subscription import Subscription
from radiople.model.user import User

from sqlalchemy import func
from sqlalchemy import desc
from sqlalchemy.orm import joinedload


class SubscriptionService(Service):

    __model__ = Subscription


class ApiSubscriptionService(SubscriptionService):

    def get_all_by_user_id(self, user_id):
        return Session.query(self.__model__) \
            .filter(Subscription.user_id == user_id).all()

    def exists(self, broadcast_id, user_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(Subscription.broadcast_id == broadcast_id)
            .filter(Subscription.user_id == user_id).exists()
        ).scalar()

    def get_list_by_broadcast_id(self, broadcast_id, paging):
        query = Session.query(self.__model__) \
            .select_from(Subscription) \
            .filter(Subscription.broadcast_id == broadcast_id)

        total_count = query.with_entities(
            func.count(Subscription.user_id)).scalar()

        item = query.with_entities(User) \
            .join(User, Subscription.user_id == User.id) \
            .order_by(desc(Subscription.created_at)) \
            .limit(paging.limit + 1) \
            .offset(paging.offset) \
            .all()

        cursor = paging.offset + 1 if len(item) > paging.limit else None

        return make_paging(item, total_count, cursor)

    def get_list_by_user_id(self, user_id, paging):
        query = Session.query(self.__model__) \
            .select_from(Subscription) \
            .filter(Subscription.user_id == user_id)

        total_count = query.with_entities(
            func.count(Subscription.user_id)).scalar()

        if paging.cursor:
            query = query .filter(Broadcast.latest_air_date <= paging.cursor)

        item = query.with_entities(Broadcast) \
            .join(Broadcast) \
            .options(joinedload('*', innerjoin=True)) \
            .order_by(desc(Broadcast.latest_air_date)) \
            .limit(paging.limit + 1) \
            .all()

        cursor = item[-1].latest_air_date if len(item) > paging.limit else None

        return make_paging(item[:paging.limit], total_count, cursor)


api_service = ApiSubscriptionService()
