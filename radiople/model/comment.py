# -*- coding: utf-8 -*-

from flask import request

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import Sequence

from sqlalchemy.orm import relationship

from radiople.model.common import CreatedAt
from radiople.model.user import User


COMMENT_ID_SEQ = Sequence('comment_id_seq')


class Comment(Base, CreatedAt):

    __tablename__ = 'comment'

    id = Column(Integer, COMMENT_ID_SEQ, primary_key=True,
                server_default=COMMENT_ID_SEQ.next_value())
    broadcast_id = Column(
        Integer, ForeignKey('broadcast.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(Text, nullable=False)

    user = relationship(User, uselist=False)

    @property
    def is_deletable(self):
        if hasattr(request, 'auth'):
            return self.user_id == request.auth.user_id
        return False
