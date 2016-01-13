# -*- coding: utf-8 -*-

from flask import request

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import Sequence
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import object_session
from sqlalchemy.dialects.postgresql import ARRAY

from radiople.model.broadcast import Broadcast
from radiople.model.audio import Audio
from radiople.model.history import History
from radiople.model.sb_episode import SbEpisode
from radiople.model.common import TimeStampMixin
from radiople.model.episode_like import EpisodeLike


EPISODE_ID_SEQ = Sequence('episode_id_seq')


class Episode(Base, TimeStampMixin):

    __tablename__ = 'episode'

    id = Column(Integer, EPISODE_ID_SEQ, primary_key=True,
                server_default=EPISODE_ID_SEQ.next_value())
    broadcast_id = Column(ForeignKey(
        'broadcast.id', ondelete='CASCADE'), nullable=False)
    audio_id = Column(ForeignKey('audio.id'), nullable=False)
    title = Column(String, index=True)
    subtitle = Column(String, index=True)
    guest = Column(ARRAY(String))
    is_active = Column(Boolean, nullable=False, default=True)
    air_date = Column(DateTime(timezone=True), nullable=False,
                      default=func.now(), server_default=func.now(),
                      index=True)
    description = Column(Text)
    scoreboard = relationship(SbEpisode, uselist=False, cascade="delete")
    audio = relationship(Audio, uselist=False)
    broadcast = relationship(Broadcast, uselist=False)

    __table_args__ = (
        Index('ix_episode_air_date_desc', air_date.desc()),
        UniqueConstraint(broadcast_id, air_date),
    )

    _activity = None

    @property
    def activity(self):
        if request.auth.is_guest:
            return None

        if self._activity is None:
            activity = object_session(self).query(Episode) \
                .with_entities(
                    self._is_like_as_scalar,
                    self._position_as_scalar
            ).one()

            self._activity = {
                'is_like': activity.is_like,
                'position': activity.position
            }

        return self._activity

    @property
    def _is_like_as_scalar(self):
        return object_session(self).query(
            object_session(self).query(EpisodeLike)
            .filter(EpisodeLike.episode_id == self.id)
            .filter(EpisodeLike.user_id == request.auth.user_id).exists()
        ).as_scalar().label('is_like')

    @property
    def _position_as_scalar(self):
        return object_session(self).query(History) \
            .with_entities(History.position or 0) \
            .filter(History.episode_id == self.id) \
            .filter(History.user_id == request.auth.user_id) \
            .as_scalar().label('position')
