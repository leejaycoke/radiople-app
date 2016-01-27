# -*- coding: utf-8 -*-

import mutagen

from radiople.db import Session
from radiople.service import Service

from radiople.model.audio import Audio

from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy import func


class AudioService(Service):

    __model__ = Audio

    def get_by_filename(self, filename):
        return Session.query(self.__model__) \
            .filter(Audio.filename == filename).scalar()

    def exists_by_filename(self, filename):
        return Session.query(
            Session.query(self.__model__)
            .filter(Audio.filename == filename).exists()
        ).scalar()


class ApiAudioService(AudioService):
    pass


class ConsoleAudioService(AudioService):

    __model__ = Audio

    def get_list(self, user_id, paging):
        query = Session.query(self.__model__) \
            .filter(Audio.user_id == user_id)

        if paging.q:
            query = query.filter(
                Audio.upload_filename.like('%' + paging.q + '%'))

        total_count = query.with_entities(func.count(Audio.id)).one()[0]

        sort = paging.get_sort(['id', 'name'])
        if sort == 'name':
            sort_column = Audio.upload_filename
        else:
            sort_column = Audio.id

        if paging.by == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        item = query.offset(paging.offset).limit(paging.page_size).all()

        return item, total_count

    def has_audio(self, partner_id):
        return Session.query(self.__model__) \
            .with_entities(func.count(self.__model__.id) > 0) \
            .filter(self.__model__.partner_id == partner_id).one()[0]

    def search_by_upload_filename(self, partner_id, q):
        return Session.query(self.__model__) \
            .filter(self.__model__.partner_id == partner_id) \
            .filter(self.__model__.upload_filename.like('%' + q + '%')) \
            .order_by(desc(self.__model__.id)) \
            .limit(10).all()


service = AudioService()
api_service = ApiAudioService()
console_service = ConsoleAudioService()
