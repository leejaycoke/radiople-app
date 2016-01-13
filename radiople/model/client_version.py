# -*- coding: utf-8 -*-

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import PrimaryKeyConstraint

from radiople.model.common import TimeStampMixin


class ClientVersion(Base, TimeStampMixin):

    __tablename__ = 'client_version'
    __table_args__ = (PrimaryKeyConstraint('os', 'app_version'),)

    os = Column(String, nullable=False)
    app_version = Column(String, nullable=False)
    is_force = Column(
        Boolean, nullable=False, default=False, server_default='False')
    is_active = Column(
        Boolean, nullable=False, default=True, server_default='True')

    @property
    def has_update(self):
        return True
