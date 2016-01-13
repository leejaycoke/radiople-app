# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractproperty

from sqlalchemy.orm import joinedload

from radiople.db import Session


class Service(object):

    __model__ = None

    def get(self, key, with_entities=False):
        query = Session.query(self.__model__)
        if with_entities:
            return query.options(joinedload('*', innerjoin=True)) \
                .get(key)
        return query.get(key)

    def insert(self, **kwargs):
        model = self.__model__()

        for k, v in kwargs.items():
            setattr(model, k, v)

        return self.save(model)

    def update(self, model, **kwargs):
        for k, v in kwargs.items():
            setattr(model, k, v)

        return self.save(model)

    def delete(self, model):
        Session.delete(model)
        Session.commit()

    def save(self, model):
        Session.add(model)
        Session.commit()
        return model

    def set_dynamic_columns(self, item):
        names = [query.name for query in self.user_properties]

        if isinstance(item, list):
            cleaned = []

            for row in item:
                for name in names:
                    setattr(row[0], name, getattr(row, name, None))
                cleaned.append(row[0])
            return cleaned

        for name in names:
            setattr(item[0], name, getattr(item, name, None))

        return item[0]

    @abstractproperty
    def user_properties(self):
        raise NotImplemented


class RedisService(object):
    pass
