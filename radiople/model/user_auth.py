# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey

from radiople.model.common import TimeStampMixin


class UserAuth(Base, TimeStampMixin):

    __tablename__ = 'user_auth'

    user_id = Column(ForeignKey(
        'user.id', ondelete='CASCADE'), primary_key=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
