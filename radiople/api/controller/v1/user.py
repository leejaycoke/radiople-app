# -*- coding: utf-8 -*-

from radiople.api.controller import api_v1

from flask import request

from radiople.worker import email as email_worker

from radiople.libs.response import json_response
from radiople.libs.permission import ApiAuthorization

from radiople.api.common import get_paging
from radiople.api.common import make_paging
from radiople.api.common import extract_user_agent

from radiople.model.user import UserInfo
from radiople.model.role import Role
from radiople.model.settings import PlayerFinishActivity
from radiople.model.settings import SkipTime

from radiople.service.crypto import email_validation_token_service
from radiople.service.user import api_service as user_service
from radiople.service.settings import api_service as settings_service
from radiople.service.device import api_service as device_service
from radiople.service.history import api_service as history_service
from radiople.service.subscription import api_service as subscription_service
from radiople.service.notification import api_service as notification_service
from radiople.service.crypto import password_service
from radiople.service.user_auth import api_service as user_auth_service

from radiople.api.response.v1.user import UserResponse
from radiople.api.response.v1.user import UserPrivateResponse
from radiople.api.response.v1.broadcast import BroadcastListResponse
from radiople.api.response.v1.settings import SettingsResponse
from radiople.api.response.v1.notification import NotificationListResponse
from radiople.api.response.v1.episode import EpisodeListResponse
from radiople.api.response.v1.history import HistoryListResponse

from radiople.api.form.user import UserEditPasswordForm
from radiople.api.form.user import UserEditEmailForm
from radiople.api.form.user import UserEditNicknameForm
from radiople.api.form.user import UserEditProfileImageForm

from radiople.exceptions import BadRequest
from radiople.exceptions import NotFound
from radiople.exceptions import Unauthorized
from radiople.exceptions import AccessDenied
from radiople.exceptions import Conflict


@api_v1.route('/user/<int:user_id>', methods=['GET'])
@api_v1.route('/user/me', methods=['GET'])
@ApiAuthorization(Role.ALL)
@json_response(UserResponse)
def user_get(user_id=None):
    user_id = user_id or request.auth.user_id

    user = user_service.get(user_id)
    if not user:
        raise NotFound("존재하지 않는 사용자입니다.")

    return user


@api_v1.route('/user/<int:user_id>/<string:info>', methods=['PUT'])
@ApiAuthorization(Role.ALL)
@json_response()
def user_put(user_id=None, info=UserInfo.PASSWORD):
    if info not in UserInfo.ALL:
        raise BadRequest

    if info == UserInfo.PASSWORD:
        form = UserEditPasswordForm(request.form)
        if not form.validate():
            raise BadRequest(form.error_message)

        user_auth = user_auth_service.get(user_id)

        current_password = form.data['current_password']

        if not password_service.match(
                user_auth.password, user_auth.salt, current_password):
            raise NotFound("현재 비밀번호가 일치하지 않습니다.")

        password, salt = password_service.hash(form.data['new_password'])
        user_auth_service.update(user_auth, password=password, salt=salt)

    elif info == UserInfo.EMAIL:
        form = UserEditEmailForm(request.form)
        if not form.validate():
            raise BadRequest(form.error_message)

        user = user_service.get(user_id)
        if user.email == form.data['email']:
            raise BadRequest("현재 이메일 주소와 동일합니다.")

        if user_service.exists_email(form.data['email']):
            raise Conflict("이미 존재하는 이메일 주소입니다.")

        user_service.update(user, email=form.data['email'], is_verified=False)

        token, expires_at, _ = email_validation_token_service.issue(
            user_id=user.id, email=user.email)

        email_worker.send_email_validation.delay(user.id, token)

    elif info == UserInfo.NICKNAME:
        form = UserEditNicknameForm(request.form)
        if not form.validate():
            raise BadRequest(form.error_message)

        user = user_service.get(user_id)
        if user.nickname == form.data['nickname']:
            raise BadRequest("현재 닉네임과 동일합니다.")

        if user_service.exists_nickname(form.data['nickname']):
            raise Conflict("이미 존재하는 닉네임입니다.")

        user_service.update(user, nickname=form.data['nickname'])

    elif info == UserInfo.PROFILE_IMAGE:
        form = UserEditProfileImageForm(request.form)
        if not form.validate():
            raise BadRequest(form.error_message)

        user = user_service.get(user_id)
        user_service.update(user, profile_image=form.data['profile_image'])


@api_v1.route('/user/<int:user_id>/device', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response()
def user_device_put(user_id):
    user_agent = extract_user_agent()

    push_token = request.form.get('push_token', '').strip()
    if push_token == '':
        raise BadRequest

    data = {
        'push_token': push_token,
        'app_version': user_agent.get('app_version'),
        'os': user_agent.get('os'),
        'os_version': user_agent.get('os_version'),
        'device_model': user_agent.get('device_model'),
        'provider': user_agent.get('provider'),
    }

    current = device_service.get_by_push_token(push_token)
    if current:
        device_service.update(current, user_id=user_id, **data)
    else:
        device_service.insert(user_id=user_id, **data)


@api_v1.route('/user/<int:user_id>/subscription', methods=['GET'])
@api_v1.route('/user/me/subscription', methods=['GET'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response(BroadcastListResponse)
def user_subscription_get(user_id=None):
    user_id = user_id or request.auth.user_id
    paging = get_paging()
    item = subscription_service.get_list_by_user_id(user_id, paging)
    return item


@api_v1.route('/user/<int:user_id>/settings', methods=['GET'])
@api_v1.route('/user/me/settings', methods=['GET'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response(SettingsResponse)
def user_settings_get(user_id=None):
    user_id = user_id or request.auth.user_id
    settings = settings_service.get(user_id)
    return settings


@api_v1.route('/user/<int:user_id>/settings', methods=['PUT'])
@api_v1.route('/user/me/settings', methods=['PUT'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response()
def user_settings_put(user_id=None):
    user_id = user_id or request.auth.user_id

    data = {}

    if 'is_ad_push_active' in request.form:
        data['is_ad_push_active'] = request.form['is_ad_push_active'] == '1'

    if 'is_subscription_push_active' in request.form:
        data['is_subscription_push_active'] = request.form[
            'is_subscription_push_active'] == '1'

    if 'is_user_push_active' in request.form:
        data['is_user_push_active'] = request.form[
            'is_user_push_active'] == '1'

    if 'is_mobile_network_active' in request.form:
        data['is_mobile_network_active'] = request.form[
            'is_mobile_network_active'] == '1'

    if 'player_finish_activity' in request.form:
        if request.form['player_finish_activity'] in PlayerFinishActivity.ALL:
            data['player_finish_activity'] = request.form[
                'player_finish_activity']

    if 'skip_seconds' in request.form:
        if request.form['skip_seconds'] in SkipTime.ALL:
            data['skip_seconds'] = request.form['skip_seconds']

    current = settings_service.get(user_id)
    settings_service.update(current, **data)


@api_v1.route('/user/<int:user_id>/notification', methods=['GET'])
@api_v1.route('/user/me/notification', methods=['GET'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response(NotificationListResponse)
def user_notification_get(user_id=None):
    user_id = user_id or request.auth.user_id

    paging = get_paging()
    item, total_count, cursor = notification_service.get_list_by_user_id(
        user_id, paging)

    response = make_paging(item, total_count, cursor)

    return response


@api_v1.route('/user/<int:user_id>/history', methods=['GET'])
@api_v1.route('/user/me/history', methods=['GET'])
@ApiAuthorization(Role.ALL, disallow=[Role.GUEST], required_me=True)
@json_response(HistoryListResponse)
def episode_history_get(user_id=None):
    user_id = user_id or request.auth.user_id

    paging = get_paging()
    item, total_count, cursor = history_service.get_list(user_id, paging)

    response = make_paging(item, total_count, cursor)

    return response
