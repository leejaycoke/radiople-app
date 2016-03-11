# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import TimeStampMixin


class SearchHistory(Base, TimeStampMixin):

    __tablename__ = 'search_history'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'keyword'), )

    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    keyword = Column(String, nullable=False, index=True)
