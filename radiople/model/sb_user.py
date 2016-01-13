# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from radiople.model.common import TimeStampMixin


class SbUser(Base, TimeStampMixin):

    __tablename__ = 'sb_user'

    user_id = Column(ForeignKey(
        'user.id', ondelete='CASCADE'), primary_key=True)
    comment_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    like_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    subscribe_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    download_count = Column(
        Integer, nullable=False, default=0, server_default="0")
    play_count = Column(Integer, nullable=False, default=0, server_default="0")
    score = Column(Integer, nullable=False, default=0, server_default="0")
