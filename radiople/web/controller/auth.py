# -*- coding: utf-8 -*-

from flask import request

from radiople.web.controller import bp_auth

from radiople.libs.response import view_response
from radiople.libs.response import json_response

from radiople.model.email_auth import EmailAuthUsage

from radiople.service.crypto import password_service
from radiople.service.crypto import email_validation_token_service
from radiople.service.crypto import find_password_token_service
from radiople.service.user import web_service as user_service
from radiople.service.user_auth import web_service as user_auth_service
from radiople.service.email_auth import web_service as email_auth_service

from radiople.web.form.auth import ResetPasswordForm

from radiople.exceptions import ExpiredToken
from radiople.exceptions import Unauthorized
from radiople.exceptions import BadRequest
from radiople.exceptions import Gone


@bp_auth.route('/register', methods=['GET'])
@view_response('auth/register.html')
def register_get():
    pass


@bp_auth.route('/email-validation', methods=['GET'])
@view_response('auth/email-validation.html')
def email_validation_verify_get():
    access_token = request.args.get('access_token')
    if not access_token or access_token.strip() == '':
        pass

    try:
        attrs = email_validation_token_service.extract(access_token)
    except ExpiredToken:
        return {'error': '인증시간이 만료되었습니다.'}
    except Exception:
        return {'error': '잘못된 정보입니다. 다시 이메일 인증을 요청하시기 바랍니다.'}

    user = user_service.get(attrs['user_id'])
    if not user:
        return {'error': '사용자 정보를 확인할 수 없습니다.'}

    if user.is_verified:
        return {'error': '이미 이메일주소 인증을 받으셨습니다.'}

    if user.email != attrs.get('email'):
        return {'error': '인증 요청 후 이메일 주소를 변경하셨기 때문에 다시 인증을 요청하셔야 합니다.'}

    user_service.update(user, is_verified=True)


@bp_auth.route('/reset-password', methods=['GET'])
@view_response('auth/reset-password.html')
def reset_password_get():
    access_token = request.args.get('access_token')
    if not access_token or access_token.strip() == '':
        return {'error': '잘못된 정보입니다.'}

    try:
        attrs = find_password_token_service.extract(access_token)
    except ExpiredToken:
        return {'error': '인증시간이 만료되었습니다.'}
    except Exception:
        return {'error': '잘못된 정보입니다.'}

    user = user_service.get(attrs['user_id'])
    if not user:
        return {'error': '잘못된 정보입니다.'}

    if not email_auth_service.exists(user.id, EmailAuthUsage.FIND_PASSWORD,
                                     access_token):
        return {'error': '잘못된 정보입니다.'}


@bp_auth.route('/reset-password', methods=['POST'])
@json_response()
def reset_password_post():
    access_token = request.args.get('access_token')
    if not access_token or access_token.strip() == '':
        return {'error': '잘못된 정보입니다.'}

    try:
        attrs = find_password_token_service.extract(access_token)
    except ExpiredToken:
        raise Gone("인증시간이 만료되었습니다.")
    except Exception:
        return Unauthorized("잘못된 정보입니다.")

    user = user_service.get(attrs['user_id'])
    if not user:
        raise Unauthorized("잘못된 정보입니다.")

    current = email_auth_service.find(
        user.id, EmailAuthUsage.FIND_PASSWORD, access_token)

    if not current:
        raise Unauthorized("잘못된 정보입니다.")

    form = ResetPasswordForm(request.form)
    if not form.validate():
        raise BadRequest(form.error_message)

    current = user_auth_service.get(attrs['user_id'])
    hashed_password, salt = password_service.hash(form.data['password'])

    user_auth_service.update(current, password=hashed_password, salt=salt)

    email_auth_service.update(current, is_discarded=True)
