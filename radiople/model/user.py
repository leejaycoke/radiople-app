# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Boolean

from sqlalchemy.orm import relationship

from radiople.model.common import TimeStampMixin
from radiople.model.sb_user import SbUser
from radiople.model.role import Role

USER_ID_SEQ = Sequence('user_id_seq')


class UserInfo(object):

    EMAIL = 'email'
    PASSWORD = 'password'
    PROFILE_IMAGE = 'profile_image'
    NICKNAME = 'nickname'
    ALL = [EMAIL, PASSWORD, PROFILE_IMAGE, NICKNAME]


class User(Base, TimeStampMixin):

    __tablename__ = 'user'

    id = Column(Integer, USER_ID_SEQ, primary_key=True,
                server_default=USER_ID_SEQ.next_value())
    nickname = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    profile_image = Column(String)
    is_verified = Column(Boolean, default=False, server_default="False")
    is_block = Column(Boolean, default=False, server_default="False")
    role = Column(String, nullable=False, default=Role.USER,
                  server_default=Role.USER)
    scoreboard = relationship(SbUser, uselist=False, cascade="delete")
