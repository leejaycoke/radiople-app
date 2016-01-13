# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.notification import Notification

from sqlalchemy import desc
from sqlalchemy import func


class NotificationService(Service):

    __model__ = Notification

    pass


class ApiNotificationService(NotificationService):

    def get_list_by_user_id(self, user_id, paging):
        query = Session.query(self.__model__) \
            .filter(Notification.user_id == user_id)

        total_count = query.with_entities(func.count(Notification.id)).scalar()

        item = query.order_by(desc(Notification.id)) \
            .limit(paging.limit + 1).all()

        cursor = item[-1].id if len(item) > paging.limit else None

        return item, total_count, cursor


service = NotificationService()
api_service = ApiNotificationService()
