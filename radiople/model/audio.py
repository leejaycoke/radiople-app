# -*- coding: utf-8 -*-

from flask import request

from hurry.filesize import size
from hurry.filesize import alternative

from radiople.db import Base

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.dialects.postgresql import ARRAY

from radiople.model.common import TimeStampMixin


AUDIO_ID_SEQ = Sequence('audio_id_seq')


class Audio(Base, TimeStampMixin):

    __tablename__ = 'audio'

    id = Column(Integer, AUDIO_ID_SEQ, primary_key=True,
                server_default=AUDIO_ID_SEQ.next_value())
    upload_filename = Column(String, nullable=False)
    filename = Column(String, nullable=False, unique=True)
    path = Column(String, nullable=False)
    length = Column(DOUBLE_PRECISION, nullable=False)
    size = Column(Integer, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    bitrate = Column(Integer, nullable=False)
    mimes = Column(ARRAY(String), nullable=False)
    user_id = Column(ForeignKey('user.id', ondelete="CASCADE"))

    _link = None
    _display_length = None
    _display_bitrate = None
    _display_sample_rate = None
    _display_size = None

    @property
    def link(self):
        return self._link

    @property
    def display_length(self):
        if self._display_length is None:
            h, remainder = divmod(self.length, 3600)
            m, s = divmod(remainder, 60)
            self._display_length = '%02d:%02d:%02d' % (h, m, s)
        return self._display_length

    @property
    def display_bitrate(self):
        if self._display_bitrate is None:
            self._bitrate = '%dKbps' % (int(self.bitrate / 1000))
        return self._bitrate

    @property
    def display_sample_rate(self):
        if self._display_sample_rate is None:
            self._sample_rate = '%dHz' % (self.sample_rate)
        return self._sample_rate

    @property
    def full_filepath(self):
        """ /경로/파일명.mp3 """
        return self.path + self.filename

    @property
    def display_size(self):
        return size(self.size, system=alternative)

    @property
    def extension(self):
        if 'audio/mpeg' in self.mimes or 'audio/mp3' in self.mimes:
            return '.mp3'
        return '.unknown'
