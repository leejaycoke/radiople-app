# -*- coding: utf-8 -*-

import re

import msgpack

from flask import request

from base64 import urlsafe_b64encode
from base64 import urlsafe_b64decode

from radiople.exceptions import BadRequest


class Paging(object):

    """
    sort=정렬 지정 값 ('popular', 'rating')
    by=정렬 방식 ('desc', 'asc')
    q=검색어
    select=검색 지정 컬럼 ('title', 'subtitle', ...)
    """

    def __init__(self, *args, **kwargs):
        for key in kwargs.get('requires', []):
            if not hasattr(self, key):
                raise BadRequest("Unknown parameter requested: '%s'" % key)

            value = getattr(self, key)
            if not value or value.strip() == '':
                raise BadRequest("Required parameter: '%s'" % key)

    @property
    def offset(self):
        return (int(self.cursor) - 1) * self.limit

    @property
    def cursor(self):
        cursor = request.args.get('cursor')
        return msgpack.unpackb(urlsafe_b64decode(cursor), encoding='utf-8') \
            if cursor else None

    @property
    def sort(self):
        sort = request.args.get('sort')
        return sort

    def get_sort(self, allowed_keys):
        return self.sort if self.sort in allowed_keys else None

    @property
    def by(self):
        by = request.args.get('by')
        return by[:10] if by and by.strip() != '' else None

    @property
    def limit(self):
        return int(request.args.get('limit', 20))

    @property
    def q(self):
        q = request.args.get('q')
        return q if q and q.strip() != '' else None


def get_paging(*args, **kwargs):
    return Paging(**kwargs)


def make_paging(item, total_count, cursor=None):
    if cursor:
        try:
            cursor = urlsafe_b64encode(msgpack.packb(cursor))
        except TypeError:
            cursor = urlsafe_b64encode(msgpack.packb(str(cursor)))

    return {
        'item': item,
        'paging': {
            'total_count': total_count,
            'next': cursor
            if cursor else None
        }
    }


USER_AGENT_PATTERN = pt = re.compile(
    r"^(radiople)\/(?P<app_version>[0-9]+\.[0-9]+\.[0-9]+) (?P<os>android|ios)\/(?P<os_version>[0-9]+(\.[0-9]+)*) \((?P<device_model>.+)\/(?P<provider>.+)\)$")


def extract_user_agent():
    user_agent = request.headers.get('User-Agent')
    match = USER_AGENT_PATTERN.match(user_agent)

    return match.groupdict() if match else {}
