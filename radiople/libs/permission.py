# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from functools import wraps

from flask import request
from flask import redirect
from flask import url_for

from radiople.model.role import Role

from radiople.service.crypto import AccessTokenService
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


class Service(object):

    API = 'api'
    CONSOLE = 'console'
    WEB = 'web'
    ADMIN = 'admin'


class Auth(object):

    user_id = None
    role = None
    service = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_guest(self, **kwargs):
        return self.role == Role.GUEST

    def is_user(self, **kwargs):
        return self.role == Role.USER

    def is_dj(self, **kwargs):
        return self.role == Role.DJ


class Authorization(metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        roles = args[0] if isinstance(args[0], list) else args
        self.roles = set(roles) - set(kwargs.get('disallow', []))
        self.position = kwargs.get('position', self.default_position)
        self.expired_ok = kwargs.get('expired_ok', False)
        self.required_me = kwargs.get('required_me', False)

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                auth = self.validate(*args, **kwargs)
            except Exception as e:
                return self.fail_execute(e)

            self.success_execute(auth)

            return func(*args, **kwargs)
        return decorator

    @abstractmethod
    def success_execute(self, auth):
        pass

    @abstractmethod
    def fail_execute(self, e):
        pass

    def get_access_token(self):
        if self.position == 'form':
            return request.form.get('access_token')
        elif self.position == 'url':
            return request.args.get('access_token')
        elif self.position == 'cookie':
            return request.cookies.get('access_token')
        else:
            bearer = request.headers.get('Authorization')
            if not bearer or not bearer.startswith('Bearer '):
                return None

            access_token = bearer.replace('Bearer ', '').strip()
            return access_token if access_token != '' else None

    @abstractproperty
    def service(self):
        raise NotImplemented

    @abstractproperty
    def default_position(self):
        raise NotImplemented

    def validate(self, *args, **kwargs):
        access_token = self.get_access_token()

        if not access_token:
            if Role.GUEST in self.roles:
                return Auth(role=Role.GUEST, service=self.service)
            else:
                raise Unauthorized

        token_service = AccessTokenService()
        token_service.validate(access_token, self.expired_ok)
        data = token_service.data

        if self.required_me and data.get('user_id') != kwargs['user_id']:
            raise AccessDenied

        if data.get('service') != self.service:
            raise AccessDenied

        user = user_service.get(data.get('user_id'))
        if not user:
            raise Unauthorized

        if user.role not in self.roles:
            raise AccessDenied

        if data.get('role') != user.role:
            raise AccessDenied

        if user.is_block:
            raise AccessDenied("운영자에의해 정지되었습니다.")

        return Auth(user_id=user.id, role=user.role, service=self.service)


class ApiAuthorization(Authorization):

    @property
    def service(self):
        return Service.API

    @property
    def default_position(self):
        return Position.AUTHORIZATION

    def success_execute(self, auth):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        raise e


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
