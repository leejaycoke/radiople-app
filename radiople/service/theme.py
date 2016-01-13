# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.theme import Theme

from radiople.api.common import make_paging

from sqlalchemy import func
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import tuple_

from sqlalchemy.orm import joinedload


class ThemeService(Service):

    __model__ = Theme


class ApiThemeService(ThemeService):

    def get_all(self):
        return Session.query(self.__model__) \
            .filter(Theme.is_active) \
            .order_by(asc(Theme.seq)).all()

api_service = ApiThemeService()
