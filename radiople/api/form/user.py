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


class UserRegisterForm(BaseForm):

    email = StringField(u"이메일 주소", [
        DataRequired(message=u"이메일 주소를 입력해주세요."),
        Email(message="이메일주소가 옳바르지 않습니다.")
    ])

    password = PasswordField('비밀번호', [
        DataRequired(message=u"비밀번호를 입력해주세요."),
        Password(message=u"비밀번호는 숫자,영어만 사용할 수 있습니다."),
        Length(min=8, max=30, message="비밀번호는 8~30글자로 입력해주세요."),
    ])

    nickname = StringField("닉네임", [
        DataRequired(message=u"닉네임을 입력해주세요."),
        Nickname(message=u"닉네임은 한글,영어,숫자만 사용할 수 있습니다."),
        Length(min=3, max=10, message="닉네임을 2~8글자로 입력해주세요.")
    ])


class UserDeviceForm(BaseForm):

    push_token = StringField(u"푸시 토큰", [
        Optional(strip_whitespace=True),
    ])


class UserEditPasswordForm(BaseForm):

    current_password = PasswordField('현재 비밀번호', [
        DataRequired(message=u"현재 비밀번호를 입력해주세요."),
    ])

    new_password = PasswordField('새로운 비밀번호', [
        DataRequired(message=u"새로운 비밀번호를 입력해주세요."),
        Password(message=u"비밀번호는 숫자,영어만 사용할 수 있습니다."),
        Length(min=6, max=30, message="비밀번호는 6~30글자로 입력해주세요."),
    ])


class UserEditEmailForm(BaseForm):

    email = StringField(u"이메일 주소", [
        DataRequired(message=u"이메일 주소를 입력해주세요."),
        Email(message="이메일주소가 옳바르지 않습니다.")
    ])


class UserEditNicknameForm(BaseForm):

    nickname = StringField("닉네임", [
        DataRequired(message=u"닉네임을 입력해주세요."),
        Nickname(message=u"닉네임은 한글,영어,숫자만 사용할 수 있습니다."),
        Length(min=2, max=8, message="닉네임을 2~8글자로 입력해주세요.")
    ])


class UserEditProfileImageForm(BaseForm):

    profile_image = StringField(u"프로필 이미지", [
        DataRequired(message=u"프로필 이미지 주소를 입력해주세요."),
        URL(message=u"프로필 이미지 주소가 옳바르지 않습니다.")
    ])
