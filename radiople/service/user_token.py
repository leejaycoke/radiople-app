# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.user_token import UserToken


class UserTokenService(Service):

    __model__ = UserToken


class WebUserTokenService(UserTokenService):

    pass


class ApiUserTokenService(UserTokenService):

    pass


class ConsoleUserTokenService(UserTokenService):

    pass


service = UserTokenService()
api_service = ApiUserTokenService()
web_service = WebUserTokenService()
console_service = ConsoleUserTokenService()
