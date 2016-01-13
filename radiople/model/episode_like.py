# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import CreatedAt


class EpisodeLike(Base, CreatedAt):

    __tablename__ = 'episode_like'
    __table_args__ = (
        PrimaryKeyConstraint('episode_id', 'user_id'),
    )

    episode_id = Column(ForeignKey(
        'episode.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, index=True)
