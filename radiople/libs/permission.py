# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from functools import wraps

from flask import request
from flask import redirect
from flask import url_for

from radiople.service.crypto import api_token_service
from radiople.service.crypto import console_token_service

from radiople.service.user import service as user_service
from radiople.service.user_token import service as user_token_service
from radiople.service.broadcast import service as broadcast_service
from radiople.service.user_broadcast import service as user_broadcast_service

from radiople.exceptions import Unauthorized
from radiople.exceptions import InvalidToken
from radiople.exceptions import AccessDenied
from radiople.exceptions import BadRequest


class Position(object):

    FORM = 'form'
    URL = 'url'
    AUTHORIZATION = 'authorization'
    COOKIE = 'cookie'


class Auth(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Permission(metaclass=ABCMeta):

    _access_token = None
    service = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                self.before_execute(*args, **kwargs)
                auth = self.validate(*args, **kwargs)
            except Exception as e:
                if self.kwargs.get('guest_ok'):
                    setattr(request, 'auth', Auth(is_guest=True))
                else:
                    return self.fail_execute(e)
            else:
                self.success_execute(auth, *args, **kwargs)

            return func(*args, **kwargs)
        return decorator

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token

        position = self.kwargs.get('position', self.default_position)

        if position == Position.AUTHORIZATION:
            bearer = request.headers.get('Authorization')
            if not bearer:
                raise Unauthorized

            if not bearer.startswith('Bearer '):
                raise Unauthorized

            return bearer.split(' ')[1]

        elif position == Position.URL:
            return request.args.get('access_token')

        elif position == Position.FORM:
            return request.form.get('access_token')

        else:
            return request.cookies.get('access_token')

    @abstractproperty
    def token_service(self):
        raise NotImplemented

    @abstractmethod
    def success_execute(self, token, *args, **kwargs):
        raise NotImplemented

    @abstractproperty
    def before_execute(self, *args, **kwargs):
        raise NotImplemented

    def validate(self, *args, **kwargs):
        expired_ok = self.kwargs.get('expired_ok', False)
        entries = self.token_service.extract(
            self.access_token, expired_ok=expired_ok)

        hashed = self.token_service.hash(self.access_token)
        user_token = user_token_service.get(
            (entries['user_id'], self.service, hashed))
        if not user_token:
            raise Unauthorized

        if self.kwargs.get('required_me', False):
            if 'user_id' not in entries or 'user_id' not in kwargs:
                raise BadRequest("required_me option needs user_id parameter")

            if entries['user_id'] != kwargs['user_id']:
                raise AccessDenied

        return Auth(is_guest=False, access_token=self.access_token, **entries)

    @abstractmethod
    def fail_execute(self, e):
        raise NotImplemented

    @abstractproperty
    def default_position(self):
        raise NotImplemented


class ApiPermission(Permission):

    """ API 사용자의 토큰 검증 """

    service = 'api'

    @property
    def token_service(self):
        return api_token_service

    @property
    def default_position(self):
        return Position.AUTHORIZATION

    @property
    def token(self):
        auth = request.headers.get('Authorization')
        if not auth.startswith('Bearer '):
            raise InvalidToken
        return auth.split('Bearer ')[1]

    def validate(self, *args, **kwargs):
        auth = super(ApiPermission, self).validate(*args, **kwargs)

        if not hasattr(auth, 'user_id') or not auth.user_id:
            raise Unauthorized

        user = user_service.get(auth.user_id)
        if not user:
            raise Unauthorized

        if user.is_block:
            raise Unauthorized("운영자에 의해 정지된 사용자입니다.")

        return auth

    def before_execute(self, *args, **kwargs):
        pass

    def success_execute(self, auth, *args, **kwargs):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        raise e


class ConsolePermission(Permission):

    """ Console 사용자의 토큰 검증 """

    service = 'console'

    @property
    def token_service(self):
        return console_token_service

    @property
    def default_position(self):
        return Position.COOKIE

    def before_execute(self, *args, **kwargs):
        pass

    def success_execute(self, auth, *args, **kwargs):
        setattr(request, 'auth', auth)

    def validate(self, *args, **kwargs):
        auth = super(ConsolePermission, self).validate(*args, **kwargs)

        if not hasattr(auth, 'user_id') or not hasattr(auth, 'broadcast_id'):
            raise Unauthorized

        if not user_broadcast_service.exists(auth.user_id, auth.broadcast_id):
            raise Unauthorized

        return auth

    def fail_execute(self, e):
        if request.is_xhr:
            raise e

        return redirect('/user/signin.html')
