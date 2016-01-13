# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.user import User


class UserService(Service):

    __model__ = User

    def exists(self, user_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(User.id == user_id).exists()
        ).scalar()

    def exists_email(self, email):
        return Session.query(
            Session.query(self.__model__)
            .filter(User.email == email).exists()
        ).scalar()

    def exists_nickname(self, nickname):
        return Session.query(
            Session.query(self.__model__)
            .filter(User.nickname == nickname).exists()
        ).scalar()

    def get_by_email(self, email):
        return Session.query(self.__model__) \
            .filter(User.email == email).scalar()

    def get_by_broadcast_id(self, broadcast_id):
        return Session.query(self.__model__) \
            .filter(User.broadcast_id == broadcast_id).scalar()


class ApiUserService(UserService):
    pass


class ConsoleUserService(UserService):
    pass


class WebUserService(UserService):
    pass


service = UserService()
api_service = ApiUserService()
console_service = ConsoleUserService()
web_service = WebUserService()
