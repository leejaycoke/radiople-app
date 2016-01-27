# -*- coding: utf-8 -*-

from urllib import parse

from hurry.filesize import size
from hurry.filesize import alternative

from radiople.db import Base
from radiople.config import config
from radiople.model.common import TimeStampMixin

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
                    'audio/mpeg3', 'video/mp4', 'application/pdf']


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
    extra = Column(MutableDict.as_mutable(JSONB))

    # _display_length = None
    # _display_bitrate = None
    # _display_sample_rate = None
    # _display_size = None
    # _container = None

    # @property
    # def display_length(self):
    #     if self._display_length is None:
    #         h, remainder = divmod(self.length, 3600)
    #         m, s = divmod(remainder, 60)
    #         self._display_length = '%02d:%02d:%02d' % (h, m, s)
    #     return self._display_length

    # @property
    # def display_bitrate(self):
    #     if self._display_bitrate is None:
    #         self._bitrate = '%dKbps' % (int(self.bitrate / 1000))
    #     return self._bitrate

    # @property
    # def display_sample_rate(self):
    #     if self._display_sample_rate is None:
    #         self._sample_rate = '%dHz' % (self.sample_rate)
    #     return self._sample_rate

    # @property
    # def display_size(self):
    #     if self._display_size is None:
    #         self._display_size = size(self.size, system=alternative)
    #     return self._display_size

    # @property
    # def extension(self):
    #     return self.filename.rsplit('.', 1)[1]

    # @property
    # def container(self):
    #     if self._container is None:
    #         p = parse.urlparse(self.url)
    #         self._container = AUDIO_CONTAINER + \
    #             p.path.replace(self.filename, '')
    #     return self._container
