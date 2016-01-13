# -*- coding: utf-8 -*-

from flask import request
from flask import redirect
from flask import url_for
from flask import make_response

from radiople.libs.response import view_response
from radiople.libs.response import json_response

from radiople.libs.permission import ConsolePermission

from radiople.model.user_token import UserTokenUsage

from radiople.service.crypto import password_service
from radiople.service.crypto import console_token_service
from radiople.service.user_auth import console_service as user_auth_service
from radiople.service.user_broadcast import console_service as user_broadcast_service
from radiople.service.user_token import console_service as user_token_service

from radiople.exceptions import NotFound
from radiople.exceptions import BadRequest

from radiople.console.controller import bp_user

from radiople.console.form.auth import AuthLoginForm


@bp_user.route('/signin.html', methods=['GET'])
@ConsolePermission(guest_ok=True)
@view_response('user/signin.html', bp=bp_user)
def signin_html():
    if not request.auth.is_guest:
        return redirect(url_for('bp_dashboard.index_html'))


@bp_user.route('/signin', methods=['POST'])
@json_response()
def signin():
    form = AuthLoginForm(request.form)
    if not form.validate():
        raise BadRequest(form.error_message)

    user_auth = user_auth_service.get_by_email(form.data['email'])
    if not user_auth:
        raise NotFound("이메일 혹은 비밀번호가 옳바르지 않습니다.")

    if not password_service.match(
            user_auth.password, user_auth.salt, form.data['password']):
        raise NotFound("이메일 혹은 비밀번호가 옳바르지 않습니다.")

    user_broadcast = user_broadcast_service.get_by_user_id(user_auth.user_id)
    if not user_broadcast:
        raise NotFound("방송국 신청 사용자가 아닙니다.")

    access_token, expires_at, hashed = console_token_service.issue(
        user_id=user_auth.user_id, broadcast_id=user_broadcast.broadcast_id)

    user_token_service.insert(
        user_id=user_auth.user_id,
        usage=UserTokenUsage.CONSOLE,
        token=hashed,
        expires_at=expires_at,
    )

    response = make_response()
    response.set_cookie('access_token', access_token)

    return response


@bp_user.route('/signout', methods=['GET'])
@ConsolePermission(guest_ok=True)
def signout():
    response = make_response(redirect(url_for('bp_user.signin_html')))
    response.set_cookie('access_token', '')

    hashed = console_token_service.hash(request.auth.access_token)

    user_token = user_token_service.get((
        request.auth.user_id,
        UserTokenUsage.CONSOLE,
        hashed
    ))

    user_token_service.delete(user_token)

    return response
