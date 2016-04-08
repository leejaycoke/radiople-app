# -*- coding: utf-8 -*-

from flask import request

from radiople.api.controller import api_v1

from radiople.api.common import get_paging
from radiople.api.common import make_paging

from radiople.api.response.v1.broadcast import BroadcastListResponse
from radiople.api.response.v1.search_history import SearchHistoryListResponse

from radiople.libs.permission import ApiAuthorization
from radiople.libs.response import json_response

from radiople.model.role import Role

from radiople.service.broadcast import api_service as broadcast_service
from radiople.service.search_history import api_service as search_history_service

from radiople.exceptions import ServerError


@api_v1.route('/search/broadcast', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(BroadcastListResponse)
def search_broadcast_get():
    paging = get_paging(requires=['q'])

    item, total_count, cursor = broadcast_service.get_list_by_search(paging)

    if item and not request.auth.is_guest():
        search_history_service.insert(
            user_id=request.auth.user_id, keyword=paging.q)

    response = make_paging(item, total_count, cursor)

    return response


@api_v1.route('/search/history', methods=['GET'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(SearchHistoryListResponse)
def search_history_get():
    paging = get_paging()

    if not paging.q:
        item, total_count, cursor = search_history_service.get_all_list(
            request.auth.user_id)
    else:
        item, total_count, cursor = search_history_service.get_list(
            request.auth.user_id, paging)

    response = make_paging(item, total_count, cursor)
    response['keyword'] = paging.q

    return response


@api_v1.route('/search/history', methods=['DELETE'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def search_history_delete():
    result = search_history_service.delete_all_by_user_id(
        request.auth.user_id)

    if not result:
        raise ServerError
