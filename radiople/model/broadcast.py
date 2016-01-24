# -*- coding: utf-8 -*-

from flask import request

from radiople.db import Base
from radiople.db import Session

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import exists
from sqlalchemy import and_

from sqlalchemy.orm import relationship
from sqlalchemy.orm import object_session

from sqlalchemy.dialects.postgresql import ARRAY

from radiople.model.common import TimeStampMixin
from radiople.model.category import Category
from radiople.model.subscription import Subscription
from radiople.model.rating import Rating
from radiople.model.podbbang import Podbbang


BROADCAST_ID_SEQ = Sequence('broadcast_id_seq')


class Broadcast(Base, TimeStampMixin):

    __tablename__ = 'broadcast'

    id = Column(Integer, BROADCAST_ID_SEQ, primary_key=True,
                server_default=BROADCAST_ID_SEQ.next_value())
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    title = Column(String, nullable=False, index=True)
    subtitle = Column(String, index=True)
    casting = Column(ARRAY(String), nullable=False)
    icon_image = Column(String)
    cover_image = Column(String)
    latest_air_date = Column(DateTime(timezone=True), index=True)
    start_at = Column(Date)
    notice = Column(Text)
    link = Column(String)
    category_id = Column(ForeignKey(Category.id), index=True)
    description = Column(Text)
    scoreboard = relationship('SbBroadcast', uselist=False, cascade="delete")
    category = relationship('Category', uselist=False)

    _activity = None

    @property
    def activity(self):
        if request.auth.is_guest:
            return None

        if self._activity is None:
            activity = object_session(self).query(Broadcast) \
                .with_entities(
                    self._is_subscriber_as_scalar,
                    self._rating_point_as_scalar,
            ).one()

            self._activity = {
                'is_subscriber': activity.is_subscriber,
                'rating_point': activity.rating_point
            }

        return self._activity

    @property
    def _is_subscriber_as_scalar(self):
        return object_session(self).query(
            object_session(self).query(Subscription)
            .filter(Subscription.broadcast_id == self.id)
            .filter(Subscription.user_id == request.auth.user_id)
            .exists()
        ).as_scalar().label('is_subscriber')

    @property
    def _rating_point_as_scalar(self):
        return object_session(self).query(Rating) \
            .with_entities(Rating.point) \
            .filter(Rating.broadcast_id == self.id) \
            .filter(Rating.user_id == request.auth.user_id) \
            .as_scalar().label('rating_point')
