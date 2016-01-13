# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Boolean

from radiople.model.common import TimeStampMixin


THEME_ID_SEQ = Sequence('theme_id_seq')


class Theme(Base, TimeStampMixin):

    __tablename__ = 'theme'

    id = Column(Integer, THEME_ID_SEQ, primary_key=True,
                server_default=THEME_ID_SEQ.next_value())
    title = Column(String, nullable=False)
    seq = Column(Integer, nullable=False, unique=True)
    is_active = Column(
        Boolean, nullable=False, default=False, server_default='False')
