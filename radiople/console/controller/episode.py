# -*- coding: utf-8 -*-

from flask import request

from radiople.console.common import make_paging
from radiople.console.common import get_paging

from radiople.console.controller import bp_episode

from radiople.console.form.episode import EpisodeCreateForm
from radiople.console.form.episode import EpisodeEditForm

from radiople.console.response.episode import EpisodeResponse
from radiople.console.response.episode import EpisodeListResponse

from radiople.libs.response import view_response
from radiople.libs.response import json_response
from radiople.libs.permission import ConsoleAuthorization

from radiople.service.episode import console_service as episode_service
from radiople.service.sb_episode import console_service as sb_episode_service
from radiople.service.storage import console_service as storage_service

from radiople.exceptions import BadRequest
from radiople.exceptions import NotFound
from radiople.exceptions import AccessDenied


@bp_episode.route('/list.html', methods=['GET'])
@ConsoleAuthorization()
@view_response('episode/list.html')
def list_html():
    return


@bp_episode.route('/create.html', methods=['GET'])
@ConsoleAuthorization()
@view_response('episode/create.html')
def create_html():
    return


@bp_episode.route('/edit.html', methods=['GET'])
@ConsoleAuthorization()
@view_response('episode/edit.html')
def edit_html():
    return {'episode_id': request.args.get('episode_id')}


@bp_episode.route('', methods=['GET'])
@ConsoleAuthorization()
@json_response(EpisodeListResponse)
def get_episode_list():
    paging = get_paging()
    item, total_count = episode_service.get_list(
        request.auth.broadcast_ids[0], paging)

    response = make_paging(item, total_count, paging.page)

    return response


@bp_episode.route('/<int:episode_id>', methods=['GET'])
@ConsoleAuthorization()
@json_response(EpisodeResponse)
def get_episode(episode_id):
    episode = episode_service.get(episode_id)

    if episode.broadcast_id != request.auth.broadcast_id:
        raise AccessDenied

    return episode


@bp_episode.route('', methods=['POST'])
@ConsoleAuthorization()
@json_response()
def post():
    form = EpisodeCreateForm(request.form)
    if not form.validate():
        raise BadRequest(form.error_message)

    guest = [g.strip()
             for g in request.form.getlist('guest[]') if g.strip() != '']

    data = {
        'storage_id': form.data['storage_id'],
        'broadcast_id': request.auth.broadcast_id,
        'title': form.data['title'],
        'subtitle': form.data['subtitle'],
        'guest': guest,
        'description': form.data['description'],
        'air_date': form.data['air_date'],
        'description': form.data['description']
    }

    storage_id = storage_service.get(form.data['storage_id'])
    if not storage_id:
        raise NotFound("음원, 혹은 파일이 등록되지 않았습니다.")

    if storage_id.user_id != request.auth.user_id:
        raise AccessDenied("접근할수 없는 파일입니다.")

    episode = episode_service.insert(**data)
    sb_episode_service.insert(episode_id=episode.id)


@bp_episode.route('/<int:episode_id>', methods=['PUT'])
@ConsoleAuthorization()
@json_response()
def edit(episode_id):
    current = episode_service.get(episode_id)
    if not current:
        raise NotFound

    if current.broadcast_id != request.auth.broadcast_id:
        raise AccessDenied

    form = EpisodeEditForm(request.form)
    if not form.validate():
        raise BadRequest(form.error_message)

    guest = [g.strip()
             for g in request.form.getlist('guest[]') if g.strip() != '']

    data = {
        'broadcast_id': request.auth.broadcast_id,
        'title': form.data['title'],
        'subtitle': form.data['subtitle'],
        'guest': guest,
        'description': form.data['description'],
        'air_date': form.data['air_date'],
        'storage_id': form.data['storage_id'],
        'description': form.data['description']
    }

    storage = storage_service.get(form.data['storage_id'])
    if not storage:
        raise NotFound("등록되지 않은 파일 혹은 음원입니다.")

    if storage.user_id != request.auth.user_id:
        raise AccessDenied("접근할수 없는 파일입니다.")

    episode_service.update(current, **data)


@bp_episode.route('/<int:episode_id>', methods=['DELETE'])
@ConsoleAuthorization()
@json_response()
def delete(episode_id):
    current = episode_service.get(episode_id, with_entities=True)
    if not current:
        raise NotFound

    if current.broadcast_id != request.auth.broadcast_id:
        raise AccessDenied

    episode_service.delete(current)  # delete cascade sb_episode ...

    storage = storage_service.get(current.storage_id)
    storage_service.delete(storage)  # delete cascade episode
