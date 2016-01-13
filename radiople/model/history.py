# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from sqlalchemy.orm import relationship

from radiople.model.common import TimeStampMixin


class History(Base, TimeStampMixin):

    __tablename__ = 'history'
    __table_args__ = (PrimaryKeyConstraint('episode_id', 'user_id'),)

    episode_id = Column(ForeignKey(
        'episode.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, index=True)
    position = Column(BigInteger, nullable=False)
