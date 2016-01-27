# -*- coding: utf-8 -*-

from radiople.libs.form import BaseForm

from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.fields import TextAreaField

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from radiople.libs.validators import Date


class EpisodeCreateForm(BaseForm):

    title = StringField(u"에피소드 제목", [
        DataRequired(message=u"에피소드 제목을 입력해주세요."),
        Length(max=50, message=u"에피소드 제목은 50 글자까지 입력할 수 있습니다.")
    ])

    air_date = StringField(u"방송 날짜", [
        DataRequired(message=u"방송 날짜를 입력해주세요."),
        Date(date_format='%Y-%m-%d %H:%M', message=u"옳바르지 않은 날짜형식입니다.")
    ])

    storage_id = IntegerField(u"파일", [
        DataRequired(message=u"파일 혹은 음원이 업로드되지 않았습니다."),
    ])

    subtitle = StringField(u"에피소드 부제목", [
        Optional(),
        Length(max=50, message=u"부제목은 50 글자까지 입력할 수 있습니다.")
    ])

    description = TextAreaField(u"에피소드 설명", [
        Optional(),
        Length(min=1, max=500, message=u"에피소드 설명은 500자까지 입력할 수 있습니다.")
    ])


class EpisodeEditForm(BaseForm):

    title = StringField(u"에피소드 제목", [
        DataRequired(message=u"에피소드 제목을 입력해주세요."),
        Length(max=50, message=u"에피소드 제목은 50 글자까지 입력할 수 있습니다.")
    ])

    storage_id = IntegerField(u"파일", [
        DataRequired(message=u"파일 혹은 음원이 업로드되지 않았습니다."),
    ])

    air_date = StringField(u"방송 날짜", [
        DataRequired(message=u"방송 날짜를 입력해주세요."),
        Date(date_format='%Y-%m-%d %H:%M', message=u"옳바르지 않은 날짜형식입니다.")
    ])

    subtitle = StringField(u"에피소드 부제목", [
        Optional(),
        Length(max=50, message=u"부제목은 50 글자까지 입력할 수 있습니다.")
    ])

    description = TextAreaField(u"에피소드 설명", [
        Optional(),
        Length(min=1, max=500, message=u"에피소드 설명은 500자까지 입력할 수 있습니다.")
    ])
