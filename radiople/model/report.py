# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import ForeignKey

from radiople.model.common import CreatedAt


REPORT_ID_SEQ = Sequence('report_id_seq')


class ContentType(object):

    COMMENT = 'comment'
    EPISODE = 'episode'
    BROADCAST = 'broadcast'


class Report(Base, CreatedAt):

    __tablename__ = 'report'

    id = Column(Integer, REPORT_ID_SEQ, primary_key=True,
                server_default=REPORT_ID_SEQ.next_value())
    content_type = Column(String, nullable=False, default=ContentType.COMMENT,
                          server_default=ContentType.COMMENT)
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    message = Column(Text)
