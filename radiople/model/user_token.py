# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import TimeStampMixin


class UserTokenUsage(object):

    API = 'api'
    WEB = 'web'
    CONSOLE = 'console'
    ADMIN = 'admin'


class UserToken(Base, TimeStampMixin):

    __tablename__ = 'user_token'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'usage', 'token'), )

    usage = Column(String, nullable=False)
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
