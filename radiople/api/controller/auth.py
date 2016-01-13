# -*- coding: utf-8 -*-

from radiople.api.controller import api_auth

from flask import request

from radiople.libs.response import json_response
from radiople.libs.permission import ApiPermission

from radiople.model.user_token import UserTokenUsage
from radiople.model.email_auth import EmailAuthUsage

from radiople.service.crypto import password_service
from radiople.service.crypto import api_token_service
from radiople.service.crypto import find_password_token_service
from radiople.service.crypto import email_validation_token_service
from radiople.service.user import api_service as user_service
from radiople.service.sb_user import api_service as sb_user_service
from radiople.service.setting import api_service as setting_service
from radiople.service.user_auth import api_service as user_auth_service
from radiople.service.user_token import api_service as user_token_service
from radiople.service.email_auth import api_service as email_auth_service
from radiople.api.form.user import UserRegisterForm

from radiople.api.response.v1.auth import UserSessionResponse

from radiople.exceptions import BadRequest
from radiople.exceptions import NotFound
from radiople.exceptions import Conflict

from radiople.worker import email as email_worker


@api_auth.route('/register', methods=['POST'])
@json_response(UserSessionResponse)
def auth_register_post():
    form = UserRegisterForm(request.form)
    if not form.validate():
        raise BadRequest(form.get_error_message())

    if user_service.exists_email(form.data['email']):
        raise Conflict("이미 존재하는 이메일주소입니다.")

    if user_service.exists_nickname(form.data['nickname'].lower()):
        raise Conflict("이미 존재하는 닉네임입니다.")

    user = user_service.insert(**form.data)
    sb_user_service.insert(user_id=user.id)

    hashed_password, salt = password_service.hash(form.data['password'])
    user_auth_service.insert(
        user_id=user.id, password=hashed_password, salt=salt)

    access_token, expires_at, hashed = api_token_service.issue(user_id=user.id)

    user_token_service.insert(usage=UserTokenUsage.API, user_id=user.id,
                              token=hashed, expires_at=expires_at)

    setting_service.insert(user_id=user.id)

    token, expires_at, _ = email_validation_token_service.issue(
        user_id=user.id, email=user.email)

    email_worker.send_email_validation.delay(user.id, token)

    return {
        'user': user,
        'session': {
            'access_token': access_token,
            'expires_at': expires_at
        }
    }


@api_auth.route('/login', methods=['POST'])
@json_response(UserSessionResponse)
def auth_login_post():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    user_auth = user_auth_service.get_by_email(email)
    if not user_auth:
        raise NotFound("아이디 혹은 비밀번호가 옳바르지 않습니다.")

    if not password_service.match(
            user_auth.password, user_auth.salt, password):
        raise NotFound("아이디 혹은 비밀번호가 옳바르지 않습니다.")

    user_id = user_auth.user_id

    access_token, expires_at, hashed = api_token_service.issue(
        user_id=user_auth.user_id)

    user_token_service.insert(usage=UserTokenUsage.API, user_id=user_id,
                              token=hashed, expires_at=expires_at)

    user = user_service.get(user_id)

    return {
        'user': user,
        'session': {
            'access_token': access_token,
            'expires_at': expires_at
        }
    }


@api_auth.route('/email-validation', methods=['POST'])
@ApiPermission()
@json_response()
def auth_email_validation_post():
    user = user_service.get(request.auth.user_id)
    if user.is_verified:
        raise Conflict("이미 이메일 인증을 받으셨습니다.")

    token, expires_at, _ = email_validation_token_service.issue(
        user_id=user.id, email=user.email)

    email_worker.send_email_validation.delay(user.id, token)


@api_auth.route('/find-password', methods=['POST'])
@json_response()
def auth_find_password_post():
    email = request.form.get('email')

    if not email or email.strip() == '':
        raise BadRequest("옳바른 이메일 주소를 입력해주세요.")

    user = user_service.get_by_email(email)

    if not user:
        raise NotFound("존재하지 않는 이메일 주소입니다.")

    token, expires_at, hashed = find_password_token_service.issue(
        user_id=user.id, email=email)

    email_auth_service.insert(
        user_id=user.id,
        usage=EmailAuthUsage.FIND_PASSWORD,
        access_token=hashed,
        expires_at=expires_at
    )

    email_worker.send_find_password.delay(user.id, token)


@api_auth.route('/refresh-access-token', methods=['GET'])
@ApiPermission(expired_ok=True)
@json_response(UserSessionResponse)
def auth_refresh_access_token_get():
    access_token, expires_at, hashed = api_token_service.issue(
        user_id=request.auth.user_id)

    user = user_service.get(request.auth.user_id)

    user_token_service.insert(usage=UserTokenUsage.API, user_id=user.id,
                              token=hashed, expires_at=expires_at)

    return {
        'user': user,
        'session': {
            'access_token': access_token,
            'expires_at': expires_at
        }
    }
