# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint


from radiople.model.common import TimeStampMixin


AGREEMENT_ID_SEQ = Sequence('agreement_id_seq')


class Type(object):

    PRIVACY = 'privacy'

    USAGE = 'usage'


class Agreement(Base, TimeStampMixin):

    __tablename__ = 'agreement'
    __table_args__ = (UniqueConstraint('type', 'version'), )

    id = Column(Integer, AGREEMENT_ID_SEQ, primary_key=True,
                server_default=AGREEMENT_ID_SEQ.next_value())
    type = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False,
                       default=True, server_default="False")
    version = Column(Date, nullable=False)
    content = Column(Text, nullable=False)
