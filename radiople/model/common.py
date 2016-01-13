# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func


class CreatedAt(object):
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=func.now(), server_default=func.now())


class UpdatedAt(object):
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        default=func.now(), server_default=func.now(),
                        onupdate=func.now())


class TimeStampMixin(CreatedAt, UpdatedAt):
    pass
