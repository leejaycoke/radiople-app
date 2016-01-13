# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from radiople.model.common import TimeStampMixin


class Podbbang(Base, TimeStampMixin):

    __tablename__ = 'podbbang'

    id = Column(Integer, primary_key=True)
    feed_url = Column(String)
    broadcast_id = Column(Integer)
