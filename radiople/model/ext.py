# -*- coding: utf-8 -*-

from sqlalchemy.ext.mutable import Mutable


class MutableList(Mutable, list):

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()

    def __setslice__(self, i, j, sequence):
        list.__setslice__(self, i, j, sequence)
        self.changed()

    def __delslice__(self, i, j):
        list.__delslice__(self, i, j)
        self.changed()

    def extend(self, iterable):
        list.extend(self, iterable)
        self.changed()

    def insert(self, index, p_object):
        list.insert(self, index, p_object)
        self.changed()

    def append(self, p_object):
        list.append(self, p_object)
        self.changed()

    def pop(self, index=None):
        list.pop(self, index)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, (set, list, tuple)):
                return MutableList(value)
            return Mutable.coerce(key, value)
        return value

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        for i in state:
            self.append(i)
