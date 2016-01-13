# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.sb_user import SbUser


class SbUserService(Service):

    __model__ = SbUser


class ApiSbUserService(SbUserService):
    pass


service = SbUserService()
api_service = ApiSbUserService()
