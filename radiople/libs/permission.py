# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from functools import wraps

from flask import request
from flask import redirect

from radiople.model.role import Role

from radiople.service.crypto import access_token_service

from radiople.service.user import service as user_service

from radiople.exceptions import Unauthorized
from radiople.exceptions import AccessDenied


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
    AUDIO = 'audio'
    IMAGE = 'image'

    ALL = [API, CONSOLE, WEB, ADMIN, AUDIO, IMAGE]


class Auth(object):

    user_id = None
    role = None
    service = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_guest(self):
        return self.role == Role.GUEST

    def is_user(self):
        return self.role == Role.USER

    def is_dj(self):
        return self.role == Role.DJ


class Authorization(metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        if args:
            roles = args[0] if isinstance(args[0], list) else args
        else:
            roles = self.default_roles
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
    def allowed_services(self):
        raise NotImplemented

    @abstractproperty
    def default_position(self):
        raise NotImplemented

    @abstractproperty
    def default_roles(self):
        raise NotImplemented

    def validate(self, *args, **kwargs):
        access_token = self.get_access_token()

        if not access_token:
            if Role.GUEST in self.roles:
                return Auth(role=Role.GUEST, service=self.service)
            else:
                raise Unauthorized

        data = access_token_service.validate(access_token, self.expired_ok)

        if self.required_me and data.get('user_id') != kwargs['user_id']:
            raise AccessDenied

        if data.get('service') not in self.allowed_services:
            raise AccessDenied

        user = user_service.get(data.get('user_id'))
        if not user:
            raise Unauthorized

        if user.role not in self.roles:
            raise AccessDenied

        if user.is_block:
            raise AccessDenied("운영자에의해 정지되었습니다.")

        return Auth(role=user.role, access_token=access_token, **data)


class ApiAuthorization(Authorization):

    @property
    def service(self):
        return Service.API

    @property
    def allowed_services(self):
        return [self.service]

    @property
    def default_position(self):
        return Position.AUTHORIZATION

    @property
    def default_roles(self):
        return Role.ALL

    def success_execute(self, auth):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        raise e


class ConsoleAuthorization(Authorization):

    @property
    def service(self):
        return Service.CONSOLE

    @property
    def allowed_services(self):
        return [self.service]

    @property
    def default_position(self):
        return Position.COOKIE

    @property
    def default_roles(self):
        return [Role.DJ]

    def success_execute(self, auth):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        if request.is_xhr:
            raise e
        return redirect('/auth/signin.html')


class AudioAuthorization(Authorization):

    @property
    def service(self):
        return Service.AUDIO

    @property
    def allowed_services(self):
        return [self.service, Service.CONSOLE]

    @property
    def default_position(self):
        return Position.URL

    @property
    def default_roles(self):
        return [Role.DJ]

    def success_execute(self, auth):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        raise e


class ImageAuthorization(Authorization):

    @property
    def service(self):
        return Service.IMAGE

    @property
    def allowed_services(self):
        return Service.ALL

    @property
    def default_position(self):
        return Position.URL

    @property
    def default_roles(self):
        return Role.ALL

    def success_execute(self, auth):
        setattr(request, 'auth', auth)

    def fail_execute(self, e):
        raise e
