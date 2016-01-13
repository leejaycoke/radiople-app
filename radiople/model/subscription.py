# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import CreatedAt
from radiople.model.user import User


class Subscription(Base, CreatedAt):

    __tablename__ = 'subscription'
    __table_args__ = (PrimaryKeyConstraint('broadcast_id', 'user_id'),)

    broadcast_id = Column(ForeignKey(
        'broadcast.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey(User.id, ondelete='CASCADE'),
                     nullable=False, index=True)
