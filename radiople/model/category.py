# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import String


CATEGORY_ID_SEQ = Sequence('category_id_seq')


class Category(Base):

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    seq = Column(Integer, nullable=False, unique=True)
