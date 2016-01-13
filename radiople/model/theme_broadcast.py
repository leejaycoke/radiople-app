# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from radiople.model.broadcast import Broadcast
from radiople.model.theme import Theme

from radiople.model.common import TimeStampMixin


class ThemeBroadcast(Base, TimeStampMixin):

    __tablename__ = 'theme_broadcast'
    __table_args__ = (
        PrimaryKeyConstraint('theme_id', 'broadcast_id'),
        UniqueConstraint('theme_id', 'seq')
    )

    theme_id = Column(ForeignKey('theme.id', ondelete='CASCADE'))
    broadcast_id = Column(ForeignKey('broadcast.id', ondelete='CASCADE'))
    seq = Column(Integer, nullable=False)
    is_active = Column(
        Boolean, nullable=False, default=True, server_default='True')

    theme = relationship(Theme, uselist=False)
    broadcast = relationship(Broadcast, uselist=False)
