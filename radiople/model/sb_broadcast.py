# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from radiople.model.broadcast import Broadcast


class SbBroadcast(Base):

    __tablename__ = 'sb_broadcast'

    broadcast_id = Column(ForeignKey(
        Broadcast.id, ondelete='CASCADE'), primary_key=True)
    comment_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    episode_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    subscriber_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    score = Column(Integer, nullable=False, default=0,
                   server_default="0", index=True)
    rating_count = Column(Integer, nullable=False,
                          default=0, server_default="0")
    rating_average = Column(DOUBLE_PRECISION, nullable=False,
                            default=0, server_default="0")

    __table_args__ = (
        Index('ix_sb_broadcast_score_desc', score.desc()),
    )
