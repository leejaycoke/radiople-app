# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.episode import Episode
from radiople.model.history import History

from sqlalchemy import func
from sqlalchemy import desc

from sqlalchemy.orm import joinedload


class HistoryService(Service):

    __model__ = History


class ApiHistoryService(HistoryService):

    def get_list(self, user_id, paging):
        query = Session.query(self.__model__) \
            .select_from(History) \
            .filter(History.user_id == user_id)

        total_count = query.with_entities(
            func.count(History.episode_id)
        ).scalar()

        item = query.with_entities(Episode) \
            .join(Episode, History.episode_id == Episode.id) \
            .options(joinedload('*', innerjoin=True)) \
            .order_by(desc(History.updated_at)) \
            .limit(100).all()

        return item, total_count, None

service = HistoryService()
api_service = ApiHistoryService()
