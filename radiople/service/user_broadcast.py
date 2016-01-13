# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.user_broadcast import UserBroadcast


class UserBroadcastService(Service):

    __model__ = UserBroadcast

    def exists(self, user_id, broadcast_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(UserBroadcast.user_id == user_id)
            .filter(UserBroadcast.broadcast_id == broadcast_id).exists()
        ).scalar()

    def get_by_user_id(self, user_id):
        return Session.query(self.__model__) \
            .filter(UserBroadcast.user_id == user_id).scalar()

    def exists_by_user_id(self, user_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(UserBroadcast.user_id == user_id).exists()
        ).scalar()

    def exists_by_broadcast_id(self, broadcast_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(UserBroadcast.broadcast_id == broadcast_id).exists()
        ).scalar()


class ApiUserBroadcastService(UserBroadcastService):

    pass


class ConsoleUserBroadcastService(UserBroadcastService):

    pass


service = UserBroadcastService()
api_service = ApiUserBroadcastService()
console_service = ConsoleUserBroadcastService()
