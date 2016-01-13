# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from radiople.api.common import get_paging
from radiople.api.common import make_paging

from radiople.libs.permission import ApiPermission

from radiople.libs.response import json_response

from radiople.service.broadcast import api_service as broadcast_service
from radiople.service.category import api_service as category_service

from radiople.api.response.v1.broadcast import BroadcastListResponse
from radiople.api.response.v1.category import CategoriesResponse

from radiople.exceptions import NotFound


@api_v1.route('/category', methods=['GET'])
@ApiPermission(guest_ok=True)
@json_response(CategoriesResponse)
def category_get():
    categories = category_service.get_all()
    return {'categories': categories}


@api_v1.route('/category/<int:category_id>/broadcast', methods=['GET'])
@ApiPermission(guest_ok=True)
@json_response(BroadcastListResponse)
def category_broadcast_get(category_id):
    if not category_service.exists(category_id):
        raise NotFound

    paging = get_paging()

    item = make_paging(
        *broadcast_service.get_list_by_category_id(category_id, paging))
    return item
