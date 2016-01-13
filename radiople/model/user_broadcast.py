# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import CreatedAt


class UserBroadcast(Base, CreatedAt):

    __tablename__ = 'user_broadcast'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'broadcast_id'), )

    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'))
    broadcast_id = Column(ForeignKey('broadcast.id', ondelete='CASCADE'))
