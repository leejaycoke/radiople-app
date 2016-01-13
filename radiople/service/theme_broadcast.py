# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.broadcast import Broadcast
from radiople.model.theme_broadcast import ThemeBroadcast

from radiople.api.common import make_paging

from sqlalchemy import func
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import tuple_

from sqlalchemy.orm import joinedload


class ThemeBroadcastService(Service):

    __model__ = ThemeBroadcast


class ApiThemeBroadcastService(ThemeBroadcastService):

    def get_all(self):
        return Session.query(self.__model__) \
            .with_entities(Broadcast) \
            .select_from(ThemeBroadcast) \
            .filter(ThemeBroadcast.is_active) \
            .order_by(asc(ThemeBroadcast.seq)) \
            .limit(limit).all()

    def get_broadcasts(self, theme_id, limit):
        return Session.query(self.__model__) \
            .with_entities(Broadcast) \
            .select_from(ThemeBroadcast) \
            .join(Broadcast) \
            .options(joinedload('*', innerjoin=True)) \
            .filter(ThemeBroadcast.theme_id == theme_id) \
            .filter(ThemeBroadcast.is_active) \
            .order_by(asc(ThemeBroadcast.seq)) \
            .limit(limit).all()

api_service = ApiThemeBroadcastService()
