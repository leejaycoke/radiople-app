# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from radiople.model.common import CreatedAt


NOTIFICATION_ID_SEQ = Sequence('notification_id_seq')


class Type(object):

    SUBSCRIPTION = 'subscription'

    AD = 'ad'


class Landing(object):

    MAIN = 'main'

    SUBSCRIPTION = 'subscription'

    BROADCAST = 'broadcast'


class Notification(Base, CreatedAt):

    __tablename__ = 'notification'

    id = Column(Integer, NOTIFICATION_ID_SEQ, primary_key=True,
                server_default=NOTIFICATION_ID_SEQ.next_value())
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'), index=True)
    type = Column(String, nullable=False)
    landing = Column(String, nullable=False)
    message = Column(String, nullable=False)
    extra = Column(MutableDict.as_mutable(JSONB), nullable=False)
