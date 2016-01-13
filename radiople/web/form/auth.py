# -*- coding: utf-8 -*-

from radiople.libs.form import BaseForm
from radiople.libs.validators import Password
from radiople.libs.validators import Nickname

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import Optional
from wtforms.validators import URL

from wtforms.fields import StringField
from wtforms.fields import PasswordField


class ResetPasswordForm(BaseForm):

    password = PasswordField('비밀번호', [
        DataRequired(message=u"비밀번호를 입력해주세요."),
        Password(message=u"비밀번호는 숫자,영어만 사용할 수 있습니다."),
        Length(min=8, max=30, message="비밀번호는 8~30글자로 입력해주세요."),
    ])
