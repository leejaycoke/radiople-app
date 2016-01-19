# -*- coding: utf-8 -*-

from flask import request

from radiople.console.controller import bp_broadcast

from radiople.exceptions import BadRequest

from radiople.libs.permission import ConsoleAuthorization
from radiople.libs.response import view_response
from radiople.libs.response import json_response

from radiople.service.category import console_service as category_service
from radiople.service.broadcast import console_service as broadcast_service

from radiople.console.form.broadcast import BroadcastCreateForm
from radiople.console.response.broadcast import BroadcastResponse


@bp_broadcast.route('/edit.html', methods=['GET'])
@ConsoleAuthorization()
@view_response('broadcast/edit.html')
def edit_html():
    return


@bp_broadcast.route('', methods=['GET'])
@ConsoleAuthorization()
@json_response(BroadcastResponse)
def json():
    broadcast = broadcast_service.get(request.auth.broadcast_id)
    return broadcast


@bp_broadcast.route('', methods=['PUT'])
@ConsoleAuthorization()
@json_response()
def edit():
    form = BroadcastCreateForm(request.form)

    if not form.validate():
        raise BadRequest(form.error_message)

    if not category_service.exists(form.data['category_id']):
        raise BadRequest("존재하지 않는 카테고리입니다.")

    casting = request.form.getlist('casting[]')
    if not casting:
        raise BadRequest("출연진을 한 명 이상 적어주세요.")

    casting = [c.strip() for c in casting if c.strip() != '']

    data = {
        'title': form.data['title'],
        'subtitle': form.data['subtitle'],
        'casting': casting,
        'category_id': form.data['category_id'],
        'description': form.data['description'],
        'icon_image': form.data['icon_image'],
        'cover_image': form.data['cover_image']
    }

    current = broadcast_service.get(request.auth.broadcast_id)

    broadcast_service.update(current, **data)
