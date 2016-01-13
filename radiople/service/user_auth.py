# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.user_auth import UserAuth
from radiople.model.user import User


class UserAuthService(Service):

    __model__ = UserAuth

    def get_by_email(self, email):
        return Session.query(self.__model__) \
            .join(User) \
            .filter(User.email == email).scalar()


class ApiUserAuthService(UserAuthService):
    pass


class WebUserAuthService(UserAuthService):
    pass


class ConsoleUserAuthService(UserAuthService):
    pass


service = UserAuthService()
api_service = ApiUserAuthService()
web_service = WebUserAuthService()
console_service = ConsoleUserAuthService()
