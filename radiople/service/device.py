# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.device import Device
from radiople.model.setting import Setting
from radiople.model.subscription import Subscription


class DeviceService(Service):

    __model__ = Device

    def get_by_push_token(self, push_token):
        return Session.query(self.__model__) \
            .filter(Device.push_token == push_token).scalar()

    def get_all_by_subsribers(self, broadcast_id):
        user_ids = Session.query(Subscription) \
            .with_entities(Subscription.user_id) \
            .join(Setting, Subscription.user_id == Setting.user_id) \
            .filter(Subscription.broadcast_id == broadcast_id) \
            .filter(Setting.subscription_push).as_scalar()

        return Session.query(self.__model__) \
            .filter(Device.user_id.in_(user_ids)).all()


class ApiDevice(DeviceService):
    pass


service = DeviceService()
api_service = ApiDevice()
