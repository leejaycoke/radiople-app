# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from radiople.model.common import TimeStampMixin


class Rating(Base, TimeStampMixin):

    __tablename__ = 'rating'
    __table_args__ = (PrimaryKeyConstraint('broadcast_id', 'user_id'),)

    broadcast_id = Column(ForeignKey(
        'broadcast.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, index=True)
    point = Column(DOUBLE_PRECISION, nullable=False)
