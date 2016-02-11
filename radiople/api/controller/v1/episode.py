# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from flask import request

from radiople.libs.response import json_response
from radiople.libs.permission import ApiAuthorization
from radiople.model.role import Role

from radiople.service.episode import api_service as episode_service
from radiople.service.sb_episode import api_service as sb_episode_service
from radiople.service.episode_like import api_service as episode_like_service
from radiople.service.history import api_service as history_service
from radiople.service.storage import api_service as storage_service

from radiople.api.response.v1.episode import EpisodeResponse

from radiople.libs.conoha import ConohaStorage

from radiople.exceptions import NotFound
from radiople.exceptions import Conflict
from radiople.exceptions import BadRequest


@api_v1.route('/episode/<int:episode_id>', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(EpisodeResponse)
def episode_get(episode_id):
    if not episode_service.exists(episode_id):
        raise NotFound("존재하지 않는 에피소드입니다.")

    episode = episode_service.get(episode_id, with_entities=True)

    return episode


@api_v1.route('/episode/<int:episode_id>/audio', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response()
def episode_playlist_get(episode_id):
    episode = episode_service.get(episode_id, with_entities=True)
    if not episode:
        raise NotFound("존재하지 않는 에피소드입니다.")

    conoha_storage = ConohaStorage()
    url = conoha_storage.generate_temp_url(episode.storage.object_path)

    return {'id': episode.storage.id, 'url': url}


@api_v1.route('/episode/<int:episode_id>/next', methods=['GET'], defaults={'switch': 'next'})
@api_v1.route('/episode/<int:episode_id>/prev', methods=['GET'], defaults={'switch': 'prev'})
@ApiAuthorization(Role.ALL)
@json_response(EpisodeResponse)
def episode_switch_get(episode_id, switch):
    if not episode_service.exists(episode_id):
        raise NotFound("존재하지않는 에피소드입니다.")

    if switch == 'next':
        episode = episode_service.get_next(episode_id)
        if not episode:
            raise NotFound("가장 최근 에피소드 입니다.")
    else:
        episode = episode_service.get_prev(episode_id)
        if not episode:
            raise NotFound("가장 처음 에피소드입니다.")

    return episode


@api_v1.route('/episode/<int:episode_id>/like', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def episode_like_put(episode_id):
    if not episode_service.exists(episode_id):
        raise NotFound("존재하지않는 에피소드입니다.")

    if episode_like_service.exists(episode_id, request.auth.user_id):
        raise Conflict("이미 좋아요하고 있습니다.")

    episode_like_service.insert(
        episode_id=episode_id, user_id=request.auth.user_id)

    sb = sb_episode_service.get(episode_id)
    sb_episode_service.update(sb, like_count=sb.like_count + 1)


@api_v1.route('/episode/<int:episode_id>/like', methods=['DELETE'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def episode_like_delete(episode_id):
    if not episode_service.exists(episode_id):
        raise NotFound("존재하지않는 에피소드입니다.")

    current = episode_like_service.get((episode_id, request.auth.user_id))
    if not current:
        raise NotFound("좋아요 하고 있지 않습니다.")

    episode_like_service.delete(current)

    sb = sb_episode_service.get(episode_id)
    sb_episode_service.update(sb, like_count=sb.like_count - 1)


@api_v1.route('/episode/<int:episode_id>/history', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def episode_history_put(episode_id):
    if not episode_service.exists(episode_id):
        raise NotFound("존재하지않는 에피소드입니다.")

    position = int(request.form.get('position', 0))
    if not position or position <= 0:
        raise BadRequest

    current = history_service.get((episode_id, request.auth.user_id))

    if current:
        history_service.update(current, position=position)
    else:
        history_service.insert(episode_id=episode_id,
                               user_id=request.auth.user_id,
                               position=position)
