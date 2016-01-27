# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from radiople.model.common import CreatedAt


STORAGE_ID_SEQ = Sequence('storage_log_id_seq')


class Service(object):

    API = 'api'
    CONSOLE = 'console'
    WEB = 'web'


class StorageLog(Base, CreatedAt):

    __tablename__ = 'storage_log'

    id = Column(Integer, STORAGE_ID_SEQ, primary_key=True,
                server_default=STORAGE_ID_SEQ.next_value())
    service = Column(String, nullable=False, default=Service.API,
                     server_default=Service.API)
    storage_id = Column(ForeignKey('storage.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    user_id = Column(Integer, nullable=False, default=0, server_default="0")
