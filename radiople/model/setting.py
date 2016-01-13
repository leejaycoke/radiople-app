# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

from radiople.model.common import TimeStampMixin


class Setting(Base, TimeStampMixin):

    __tablename__ = 'setting'

    user_id = Column(ForeignKey(
        'user.id', ondelete='CASCADE'), primary_key=True)
    all_push = Column(
        Boolean, nullable=False, default=True, server_default="True")
    subscription_push = Column(
        Boolean, nullable=False, default=True, server_default="True")
    user_push = Column(
        Boolean, nullable=False, default=True, server_default="True")
