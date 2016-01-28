# -*- coding: utf-8 -*-

from radiople.libs.form import BaseForm

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import URL

from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.fields import TextAreaField


class BroadcastCreateForm(BaseForm):

    title = StringField(u"제목", [
        DataRequired(message=u"방송 제목을 입력해주세요."),
        Length(min=1, max=30, message=u"방송 제목을 1~30 글자로 입력해주세요.")
    ])

    subtitle = StringField(u"부제목", [
        Optional(),
        Length(min=2, max=50, message=u"부제목을 2~50 글자로 입력해주세요.")
    ])

    category_id = IntegerField(u"카테고리", [
        DataRequired(message=u"카테고리를 입력해주세요.")
    ])

    description = TextAreaField(u"방송 설명", [
        Optional(),
        Length(min=1, max=500, message=u"방송 설명은 500자까지 입력할 수 있습니다.")
    ])

    icon_image = StringField(u"아이콘 이미지", [
        Optional(),
        URL(require_tld=False, message=u"아이콘 이미지가 옳바르지 않습니다.")
    ])

    cover_image = StringField(u"커버 이미지", [
        Optional(),
        URL(require_tld=False, message=u"커버 이미지가 옳바르지 않습니다.")
    ])


class NoticeForm(BaseForm):

    notice = TextAreaField(u"공지사항 내용", [
        Optional(),
        Length(min=1, max=500, message=u"1~500 글자 미만으로 입력해주세요.")
    ])
