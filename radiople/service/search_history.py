# -*- coding: utf-8 -*-

from radiople.service import Service

from radiople.model.search_history import SearchHistory


class SearchHistoryService(Service):

    __model__ = SearchHistory


class ApiSearchHistoryService(SearchHistoryService):

    pass


class ConsoleSearchHistoryService(SearchHistoryService):

    pass


service = SearchHistoryService()
api_service = ApiSearchHistoryService()
console_service = ConsoleSearchHistoryService()
