# -*- coding: utf-8 -*-

from radiople.db import Session

from datetime import datetime
from radiople.service import Service

from sqlalchemy import desc

from radiople.model.search_history import SearchHistory


class SearchHistoryService(Service):

    __model__ = SearchHistory

    def insert(self, **kwargs):
        current = self.get((kwargs['user_id'], kwargs['keyword']))
        if not current:
            return super(SearchHistoryService, self).insert(**kwargs)

        return self.update(current, updated_at=datetime.now())

    def delete_all_by_user_id(self, user_id):
        try:
            self.Session.query(self.__model__) \
                .filter(SearchHistory.user_id == user_id).delete()
            return True
        except:
            Session.rollback()
            return False


class ApiSearchHistoryService(SearchHistoryService):

    def get_all_list(self, user_id):
        item = Session.query(self.__model__) \
            .filter(SearchHistory.user_id == user_id) \
            .order_by(desc(SearchHistory.updated_at)) \
            .limit(100).all()

        return item, len(item), None

    def get_list(self, user_id, paging):
        item = Session.query(self.__model__) \
            .filter(SearchHistory.user_id == user_id) \
            .filter(SearchHistory.keyword.ilike('%' + paging.q + '%')) \
            .order_by(desc(SearchHistory.updated_at)) \
            .limit(100).all()

        return item, len(item), None


class ConsoleSearchHistoryService(SearchHistoryService):

    pass


service = SearchHistoryService()
api_service = ApiSearchHistoryService()
console_service = ConsoleSearchHistoryService()
