# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import ForeignKey

from radiople.model.common import CreatedAt


SEARCH_HISTORY_ID_SEQ = Sequence('search_history_id_seq')


class SearchHistory(Base, CreatedAt):

    __tablename__ = 'search_history'

    id = Column(Integer, SEARCH_HISTORY_ID_SEQ, primary_key=True,
                server_default=SEARCH_HISTORY_ID_SEQ.next_value())
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    keyword = Column(String, nullable=False)
