# -*- coding: utf-8 -*-

import re

from wtforms.validators import ValidationError
from datetime import datetime


class Date(object):

    def __init__(self, date_format='%Y-%m-%d', message=None):
        self.date_format = date_format or '%Y-%m-%d'
        self.message = message or u'옳바르지 않은 날짜 형식입니다.'

    def __call__(self, form, field):
        try:
            datetime.strptime(field.data, self.date_format)
        except:
            raise ValidationError(self.message)


class Password(object):

    PATTERN = re.compile(r"^[a-zA-Z0-9]+$")

    def __init__(self, message=None):
        self.message = message or u"비밀번호를 숫자,영어만 사용할 수 있습니다."

    def __call__(self, form, field):
        try:
            if not re.match(self.PATTERN, field.data):
                raise ValidationError(self.message)
        except:
            raise ValidationError(self.message)


class Nickname(object):

    PATTERN = re.compile(r"^[가-힣a-zA-Z0-9]+$")

    def __init__(self, message=None):
        self.message = message or u"닉네임은 한글,영어, 숫자만 사용할 수 있습니다."

    def __call__(self, form, field):
        try:
            if not re.match(self.PATTERN, field.data):
                raise ValidationError(self.message)
        except:
            raise ValidationError(self.message)


class AppVersion(object):

    PATTERN = re.compile(r"^([0-9]{1}\.)([0-9]{1}\.)([0-9]{1})$")

    def __init__(self, message=None):
        self.message = message or u"앱버젼이 옳바르지 않습니다."

    def __call__(self, form, field):
        try:
            if not re.match(self.PATTERN, field.data):
                raise ValidationError(self.message)
        except:
            raise ValidationError(self.message)


class Os(object):

    OS = ['android', 'ios']

    def __init__(self, message=None):
        self.message = message or u"운영체제가 옳바르지 않습니다."

    def __call__(self, form, field):
        try:
            if field.data not in self.OS:
                raise ValidationError(self.message)
        except:
            raise ValidationError(self.message)
