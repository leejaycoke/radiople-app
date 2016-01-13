# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from sqlalchemy.dialects.postgresql import ARRAY

from radiople.model.common import CreatedAt


class CacheEpisodeLike(Base):

    __tablename__ = 'cache_episode_like'

    episode_id = Column(ForeignKey(
        'episode.id', ondelete='CASCADE'), primary_key=True)
    user_ids = Column(ARRAY(Integer), nullable=False,
                      default=[], server_default='{}')
