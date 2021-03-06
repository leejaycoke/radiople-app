# -*- coding: utf-8 -*-

from flask import request

from radiople.api.common import get_paging
from radiople.api.common import make_paging

from radiople.libs.permission import ApiAuthorization
from radiople.model.role import Role
from radiople.libs.response import json_response

from radiople.model.report import ContentType

from radiople.service.broadcast import api_service as broadcast_service
from radiople.service.sb_broadcast import api_service as sb_broadcast_service
from radiople.service.episode import api_service as episode_service
from radiople.service.subscription import api_service as subscription_service
from radiople.service.comment import api_service as comment_service
from radiople.service.rating import api_service as rating_service
from radiople.service.report import api_service as report_service

from radiople.api.controller import api_v1

from radiople.api.response.v1.broadcast import BroadcastResponse
from radiople.api.response.v1.broadcast import BroadcastListResponse
from radiople.api.response.v1.comment import CommentResponse
from radiople.api.response.v1.comment import CommentListResponse
from radiople.api.response.v1.episode import EpisodeListResponse

from radiople.api.form.comment import CommentForm

from radiople.exceptions import NotFound
from radiople.exceptions import Conflict
from radiople.exceptions import BadRequest
from radiople.exceptions import Unauthorized


@api_v1.route('/broadcast', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(BroadcastListResponse)
def broadcast_list_get():
    return


@api_v1.route('/broadcast/<int:broadcast_id>', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(BroadcastResponse)
def broadcast_get(broadcast_id):
    broadcast = broadcast_service.get(broadcast_id, with_entities=True)
    if not broadcast:
        raise NotFound("존재하지 않는 방송입니다.")
    return broadcast


@api_v1.route('/broadcast/<int:broadcast_id>/episode', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(EpisodeListResponse)
def broadcast_episode_get(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    paging = get_paging()

    item, total_count, cursor = episode_service.get_list(
        broadcast_id, paging)

    response = make_paging(item, total_count, cursor)
    return response


@api_v1.route('/broadcast/<int:broadcast_id>/subscription', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(BroadcastResponse)
def subscription_put(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    if subscription_service.exists(broadcast_id, request.auth.user_id):
        raise Conflict("이미 구독하고 있습니다.")

    subscription_service.insert(
        broadcast_id=broadcast_id,
        user_id=request.auth.user_id
    )

    sb_broadcast_service.refresh_subscription_count(broadcast_id)

    broadcast = broadcast_service.get(broadcast_id, with_entities=True)

    return broadcast


@api_v1.route('/broadcast/<int:broadcast_id>/subscription', methods=['DELETE'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(BroadcastResponse)
def subscription_delete(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    current = subscription_service.get(
        (broadcast_id, request.auth.user_id))
    if not current:
        raise NotFound("아직 구독하고 있지 않습니다.")

    subscription_service.delete(current)

    sb_broadcast_service.refresh_subscription_count(broadcast_id)

    broadcast = broadcast_service.get(broadcast_id, with_entities=True)

    return broadcast


@api_v1.route('/broadcast/<int:broadcast_id>/comment', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(CommentListResponse)
def comment_get(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    paging = get_paging()
    item = comment_service.get_list(broadcast_id, paging)

    response = make_paging(*item)
    return response


@api_v1.route('/broadcast/<int:broadcast_id>/comment/<int:comment_id>/report', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def comment_report_put(broadcast_id, comment_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    if not comment_service.exists(comment_id):
        raise NotFound("존재하지 않는 댓글입니다.")

    report_service.insert(content_type=ContentType.COMMENT,
                          entity_id=comment_id,
                          user_id=request.auth.user_id)


@api_v1.route('/broadcast/<int:broadcast_id>/comment', methods=['POST'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(CommentResponse)
def comment_post(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    form = CommentForm(request.form)
    if not form.validate():
        raise BadRequest(form.get_error_message())

    comment = comment_service.insert(
        broadcast_id=broadcast_id,
        user_id=request.auth.user_id,
        content=form.data['content']
    )

    sb_broadcast_service.refresh_comment_count(broadcast_id)

    return comment


@api_v1.route('/broadcast/<int:broadcast_id>/comment/<int:comment_id>', methods=['DELETE'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response()
def comment_delete(broadcast_id, comment_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    current = comment_service.get(comment_id)
    if not current:
        raise NotFound("존재하지 않는 댓글입니다.")

    if current.broadcast_id != broadcast_id:
        raise NotFound("존재하지 않는 댓글입니다.")

    if current.user_id != request.auth.user_id:
        raise Unauthorized("본인의 댓글이 아닙니다.")

    comment_service.delete(current)

    sb_broadcast_service.refresh_comment_count(broadcast_id)


POINT_RANGE = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]


@api_v1.route('/broadcast/<int:broadcast_id>/rating', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(BroadcastResponse)
def rating_put(broadcast_id):
    point = request.form.get('point')
    if not point:
        raise BadRequest("점수를 입력해주세요.")

    point = float(point)
    if point not in POINT_RANGE:
        raise BadRequest("평가할 수 없는 점수입니다.")

    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    current = rating_service.get(
        (broadcast_id, request.auth.user_id))

    if current:
        rating_service.update(
            current,
            broadcast_id=broadcast_id,
            user_id=request.auth.user_id,
            point=point
        )
    else:
        rating_service.insert(
            broadcast_id=broadcast_id,
            user_id=request.auth.user_id,
            point=point
        )

    sb_broadcast_service.refresh_rating(broadcast_id)

    broadcast = broadcast_service.get(broadcast_id, with_entities=True)

    return broadcast


@api_v1.route('/broadcast/<int:broadcast_id>/rating', methods=['DELETE'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST])
@json_response(BroadcastResponse)
def rating_delete(broadcast_id):
    if not broadcast_service.exists(broadcast_id):
        raise NotFound("존재하지 않는 방송입니다.")

    current = rating_service.get(
        (broadcast_id, request.auth.user_id))

    if not current:
        raise NotFound("평가하지 않았습니다.")

    rating_service.delete(current)

    sb_broadcast_service.refresh_rating(broadcast_id)

    broadcast = broadcast_service.get(broadcast_id, with_entities=True)

    return broadcast
