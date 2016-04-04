# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

from radiople.model.common import TimeStampMixin


class SkipTime(object):

    SECONDS_10 = 10
    SECONDS_20 = 20
    SECONDS_30 = 30
    SECONDS_40 = 40
    SECONDS_50 = 50
    SECONDS_60 = 60

    ALL = [SECONDS_10, SECONDS_20, SECONDS_30,
           SECONDS_40, SECONDS_50, SECONDS_60]


class PlayerFinishActivity(object):

    STOP = 'stop'
    NEXT_EPISODE = 'next_episode'
    ALL = [STOP, NEXT_EPISODE]


class Settings(Base, TimeStampMixin):

    __tablename__ = 'settings'

    user_id = Column(ForeignKey(
        'user.id', ondelete='CASCADE'), primary_key=True)
    is_ad_push_active = Column(
        Boolean, nullable=False, default=True, server_default="True")
    is_subscription_push_active = Column(
        Boolean, nullable=False, default=True, server_default="True")
    is_user_push_active = Column(
        Boolean, nullable=False, default=True, server_default="True")
    is_mobile_network_active = Column(
        Boolean, nullable=False, default=False, server_default="False")
    skip_seconds = Column(Integer, nullable=False, default=SkipTime.SECONDS_30,
                          server_default=str(SkipTime.SECONDS_30))
    player_finish_activity = Column(String, nullable=False,
                                    default=PlayerFinishActivity.STOP,
                                    server_default=PlayerFinishActivity.STOP)
