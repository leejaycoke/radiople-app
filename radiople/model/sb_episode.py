# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import Index
from sqlalchemy import ForeignKey

from radiople.model.common import TimeStampMixin

EPISODE_ID_SEQ = Sequence('episode_id_seq')


class SbEpisode(Base, TimeStampMixin):

    __tablename__ = 'sb_episode'

    episode_id = Column(ForeignKey(
        'episode.id', ondelete='CASCADE'), primary_key=True)
    like_count = Column(Integer, nullable=False, default=0, server_default="0")
    download_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    play_count = Column(Integer, nullable=False, default=0, server_default="0")
    score = Column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        Index('ix_sb_episode_score_desc', score.desc()),
    )
