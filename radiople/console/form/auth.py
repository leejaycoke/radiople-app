# -*- coding: utf-8 -*-

from radiople.libs.form import BaseForm
from radiople.libs.validators import Password
from radiople.libs.validators import Nickname

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email

from wtforms.fields import StringField
from wtforms.fields import PasswordField


class AuthLoginForm(BaseForm):

    email = StringField(u"이메일 주소", [
        DataRequired(message=u"이메일 주소를 입력해주세요."),
        Email(message="이메일주소가 옳바르지 않습니다.")
    ])

    password = PasswordField('비밀번호', [
        DataRequired(message=u"비밀번호를 입력해주세요."),
    ])
