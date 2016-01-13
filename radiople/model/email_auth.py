# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import String

from radiople.model.common import CreatedAt


EMAIL_AUTH_ID_SEQ = Sequence('email_auth_id_seq')


class EmailAuthUsage(object):

    EMAIL_VALIDATION = 'email_validation'
    FIND_PASSWORD = 'find_password'


class EmailAuth(Base, CreatedAt):

    __tablename__ = 'email_auth'

    id = Column(Integer, EMAIL_AUTH_ID_SEQ, primary_key=True,
                server_default=EMAIL_AUTH_ID_SEQ.next_value())
    user_id = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    usage = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_discarded = Column(Boolean, default=False,
                          nullable=False, server_default="False")
