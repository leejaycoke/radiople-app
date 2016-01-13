# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from radiople.model.common import CreatedAt


AUDIO_LOG_ID_SEQ = Sequence('audio_log_id_seq')


class Server(object):

    API = 'api'
    CONSOLE = 'console'
    WEB = 'web'


class AudioLog(Base, CreatedAt):

    __tablename__ = 'audio_log'

    id = Column(Integer, AUDIO_LOG_ID_SEQ, primary_key=True,
                server_default=AUDIO_LOG_ID_SEQ.next_value())
    server = Column(String, nullable=False, default=Server.API,
                    server_default=Server.API)
    audio_id = Column(ForeignKey('audio.id', ondelete='CASCADE'),
                      nullable=False, index=True)
    user_id = Column(Integer, nullable=False, default=0, server_default="0")
    byte_range = Column(String, nullable=False)
