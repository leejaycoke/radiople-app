# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from radiople.libs.response import json_response
from radiople.libs.permission import ApiPermission

from radiople.service.theme import api_service as theme_service
from radiople.service.theme_broadcast import api_service as theme_broadcast_service
from radiople.service.broadcast import api_service as broadcast_service

from radiople.api.common import get_paging
from radiople.api.common import make_paging

from radiople.api.response.v1.main import NewsResponse
from radiople.api.response.v1.broadcast import BroadcastListResponse


# @cache.cached(timeout=60, key_prefix='%s')
@api_v1.route('/main/news', methods=['GET'])
@ApiPermission(guest_ok=True)
@json_response(NewsResponse)
def main_news_get():
    theme_broadcasts = []

    themes = theme_service.get_all()

    for theme in themes:
        item = {'theme': theme}
        broadcasts = theme_broadcast_service.get_broadcasts(theme.id, 2)
        item['broadcasts'] = broadcasts

        theme_broadcasts.append(item)

    if len(theme_broadcasts[0]['broadcasts']) > 1:
        theme_broadcasts[0]['broadcasts'] = theme_broadcasts[
            0]['broadcasts'][:1]

    response = {'theme_broadcasts': theme_broadcasts}

    return response


@api_v1.route('/main/ranking', methods=['GET'])
@ApiPermission(guest_ok=True)
@json_response(BroadcastListResponse)
def main_ranking_get():
    paging = get_paging()
    item, total_count, cursor = broadcast_service.get_ranking_list(paging)

    response = make_paging(item, total_count, cursor)

    return response
