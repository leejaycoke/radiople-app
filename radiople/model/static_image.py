# -*- coding: utf-8 -*-

from radiople.db import Base
from radiople.model.common import TimeStampMixin

from sqlalchemy import Column
from sqlalchemy import String


class Position(object):

    LEFT_MENU = 'left_menu'

    MAIN = 'main'

    SIGNUP = 'signup'

    LOGIN = 'login'


class StaticImage(Base, TimeStampMixin):

    __tablename__ = 'static_image'

    position = Column(String, primary_key=True)
    image = Column(String, nullable=False)
