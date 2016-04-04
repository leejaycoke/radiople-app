# -*- coding: utf-8 -*-

from hurry.filesize import size
from hurry.filesize import alternative

from radiople.db import Base
from radiople.model.common import TimeStampMixin
from radiople.config import config

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Sequence
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableDict


STORAGE_ID_SEQ = Sequence('storage_id_seq')

ACCEPTABLE_MIMES = ['audio/mp3', 'audio/mpeg', 'application/octet-stream',
                    'audio/mpeg3', 'video/mp4', 'application/pdf', 'mp3',
                    'video/mpeg4']

STORAGE_URL = config.common.storage.url
STORAGE_PATH = config.common.storage.path


class FileType(object):

    AUDIO = 'audio'
    VIDEO = 'video'
    PDF = 'pdf'
    PPT = 'ppt'
    DOC = 'doc'
    UNKNOWN = 'unknown'


class Storage(Base, TimeStampMixin):

    __tablename__ = 'storage'

    id = Column(Integer, STORAGE_ID_SEQ, primary_key=True,
                server_default=STORAGE_ID_SEQ.next_value())
    user_id = Column(ForeignKey('user.id', ondelete="CASCADE"))
    filename = Column(String, nullable=False, unique=True)
    uploaded_filename = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    mimes = Column(ARRAY(String), nullable=False)
    url = Column(String, nullable=False)
    _extra = Column('extra', MutableDict.as_mutable(JSONB))

    @property
    def extra(self):
        if not self._extra:
            return self._extra
        self._extra.update({
            'display_length': self.display_length,
            'display_bitrate': self.display_bitrate,
            'display_sample_rate': self.display_sample_rate,
            'display_size': self.display_size
        })
        return self._extra

    @extra.setter
    def extra(self, value):
        self._extra = value

    @property
    def display_length(self):
        h, remainder = divmod(self._extra.get('length'), 3600)
        m, s = divmod(remainder, 60)
        return '%02d:%02d:%02d' % (h, m, s)

    @property
    def display_bitrate(self):
        return '%dKbps' % (int(self._extra.get('bitrate') / 1000))

    @property
    def display_sample_rate(self):
        return '%dHz' % (self._extra.get('sample_rate'))

    @property
    def display_size(self):
        return size(self.size, system=alternative)

    @property
    def extension(self):
        return self.filename.rsplit('.', 1)[1]

    @property
    def object_path(self):
        return self.url.replace(STORAGE_URL + STORAGE_PATH, '')

    @property
    def file_type(self):
        if 'audio/mp3' in self.mimes or 'audio/mpeg' in self.mimes:
            return FileType.AUDIO
        elif 'audio/mp4' in self.mimes or 'vidoe/mp4' in self.mimes:
            return FileType.VIDEO
        elif 'application/pdf' in self.mimes:
            return FileType.PDF
        return FileType.UNKNOWN
