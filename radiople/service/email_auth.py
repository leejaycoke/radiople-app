# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service
from radiople.service.crypto import find_password_token_service

from radiople.model.email_auth import EmailAuth

from sqlalchemy import desc


class EmailAuthService(Service):

    __model__ = EmailAuth

    def exists(self, user_id, usage, token):
        hashed = find_password_token_service.hash(token)
        return Session.query(
            Session.query(self.__model__)
                      .filter(EmailAuth.user_id == user_id)
                      .filter(EmailAuth.usage == usage)
                      .filter(EmailAuth.access_token == hashed)
                      .filter(EmailAuth.is_discarded == False).exists()
        ).scalar()

    def find(self, user_id, usage, token):
        hashed = find_password_token_service.hash(token)
        return Session.query(self.__model__) \
                      .filter(EmailAuth.user_id == user_id) \
                      .filter(EmailAuth.usage == usage) \
                      .filter(EmailAuth.access_token == hashed).scalar()


class ApiEmailAuthService(EmailAuthService):

    def get_latest(self, user_id):
        return Session.query(self.__model__) \
            .filter(EmailAuth.user_id == user_id) \
            .order_by(desc(EmailAuth.id)).first()


class WebEmailAuthService(EmailAuthService):

    pass


class ConsoleEmailAuthService(EmailAuthService):

    pass


service = EmailAuthService()
api_service = ApiEmailAuthService()
web_service = ApiEmailAuthService()
console_service = ConsoleEmailAuthService()
