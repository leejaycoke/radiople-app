# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import UniqueConstraint

from radiople.model.common import TimeStampMixin


DEVICE_ID_SEQ = Sequence('device_id_seq')


class Device(Base, TimeStampMixin):

    __tablename__ = 'device'
    __table_args__ = (UniqueConstraint('user_id', 'push_token'),)

    id = Column(Integer, DEVICE_ID_SEQ, primary_key=True,
                server_default=DEVICE_ID_SEQ.next_value())
    user_id = Column(ForeignKey(
        'user.id', ondelete='CASCADE'), primary_key=True)
    app_version = Column(String, nullable=False)
    push_token = Column(String, nullable=False, index=True)
    provider = Column(String)
    os = Column(String, nullable=False)
    os_version = Column(String, nullable=False)
    device_model = Column(String)
    verified_at = Column(DateTime(timezone=True))

    @property
    def push_platform(self):
        return 'gcm' if self.os == 'android' else 'apns'
