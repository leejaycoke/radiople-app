# -*- coding: utf-8 -*-

from radiople.db import Base

from radiople.model.common import CreatedAt

from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict


OPENSOURCE_ID_SEQ = Sequence('opensource_id_seq')


class OS(object):

    ANDROID = 'android'

    IOS = 'ios'


class OpenSource(Base, CreatedAt):

    __tablename__ = 'opensource'
    __table_args__ = (UniqueConstraint('os', 'app_version'), )

    id = Column(Integer, OPENSOURCE_ID_SEQ, primary_key=True,
                server_default=OPENSOURCE_ID_SEQ.next_value())
    os = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False,
                       default=False, server_default="True")
    app_version = Column(String, nullable=False)
    content = Column(Text, nullable=False)
