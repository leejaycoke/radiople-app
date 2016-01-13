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
from radiople.libs.permission import ConsolePermission

from radiople.service.episode import console_service as episode_service
from radiople.service.sb_episode import console_service as sb_episode_service
from radiople.service.audio import console_service as audio_service

from radiople.exceptions import BadRequest
from radiople.exceptions import NotFound
from radiople.exceptions import AccessDenied


@bp_episode.route('/list.html', methods=['GET'])
@ConsolePermission()
@view_response('episode/list.html')
def list_html():
    return


@bp_episode.route('/create.html', methods=['GET'])
@ConsolePermission()
@view_response('episode/create.html')
def create_html():
    return


@bp_episode.route('/edit.html', methods=['GET'])
@ConsolePermission()
@view_response('episode/edit.html')
def edit_html():
    return {'episode_id': request.args.get('episode_id')}


@bp_episode.route('s', methods=['GET'])
@ConsolePermission()
@json_response()
def get_episode_list():
    paging = get_paging()
    item, total_count = episode_service.get_list(
        request.auth.broadcast_id, paging)

    response = make_paging(item, total_count, paging.page)

    response = EpisodeListResponse(response)

    return response


@bp_episode.route('/<int:episode_id>', methods=['GET'])
@ConsolePermission()
@json_response()
def get_episode(episode_id):
    episode = episode_service.get(episode_id)

    if episode.broadcast_id != request.auth.broadcast_id:
        raise AccessDenied

    return EpisodeResponse(episode)


@bp_episode.route('', methods=['POST'])
@ConsolePermission()
@json_response()
def post():
    form = EpisodeCreateForm(request.form)
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
        'audio_id': form.data['audio_id'],
        'description': form.data['description']
    }

    audio = audio_service.get(form.data['audio_id'])
    if not audio:
        raise NotFound("등록되지 않은 음원입니다.")

    if audio.user_id != request.auth.user_id:
        raise AccessDenied("접근할수 없는 음원입니다.")

    episode = episode_service.insert(**data)
    sb_episode_service.insert(episode_id=episode.id)


@bp_episode.route('/<int:episode_id>', methods=['PUT'])
@ConsolePermission()
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
        'audio_id': form.data['audio_id'],
        'description': form.data['description']
    }

    audio = audio_service.get(form.data['audio_id'])
    if not audio:
        raise NotFound("등록되지 않은 오디오입니다.")

    if audio.user_id != request.auth.user_id:
        raise AccessDenied

    episode_service.update(current, **data)


@bp_episode.route('/<int:episode_id>', methods=['DELETE'])
@ConsolePermission()
@json_response()
def delete(episode_id):
    current = episode_service.get(episode_id, with_entities=True)
    if not current:
        raise NotFound

    if current.broadcast_id != request.auth.broadcast_id:
        raise AccessDenied

    episode_service.delete(current)  # delete cascade sb_episode ...

    audio = audio_service.get(current.audio.id)
    audio_service.delete(audio)  # delete cascade episode
