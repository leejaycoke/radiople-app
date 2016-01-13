# -*- coding: utf-8 -*-

from flask import request

from radiople.api.controller import api_v1

from radiople.api.common import get_paging
from radiople.api.common import make_paging

from radiople.libs.permission import ApiPermission
from radiople.libs.response import json_response

from radiople.service.broadcast import api_service as broadcast_service
from radiople.service.search_history import api_service as search_history_service

from radiople.api.response.v1.broadcast import BroadcastListResponse


@api_v1.route('/search/broadcast', methods=['GET'])
@ApiPermission(guest_ok=True)
@json_response(BroadcastListResponse)
def search_broadcast_get():
    paging = get_paging(requires=['q'])

    if not request.auth.is_guest and not paging.cursor:
        search_history_service.insert(
            user_id=request.auth.user_id, keyword=paging.q)

    item, total_count, cursor = broadcast_service.get_list_by_search(paging)

    response = make_paging(item, total_count, cursor)

    return response
