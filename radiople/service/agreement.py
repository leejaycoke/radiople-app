# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.agreement import Agreement

from sqlalchemy import asc
from sqlalchemy import desc


class AgreementService(Service):

    __model__ = Agreement

    def get_by_type(self, type):
        return Session.query(self.__model__) \
            .filter(Agreement.type == type) \
            .order_by(desc(Agreement.version)).first()


class ApiUserService(AgreementService):
    pass


class ConsoleUserService(AgreementService):
    pass


service = AgreementService()
api_service = ApiUserService()
console_service = ConsoleUserService()
