# -*- coding: utf-8 -*-

from radiople.libs.form import BaseForm

from wtforms.validators import DataRequired
from wtforms.validators import Length

from wtforms.fields import StringField


class CommentForm(BaseForm):

    content = StringField(u"댓글 내용", [
        DataRequired(message=u"댓글 내용을 입력해주세요."),
        Length(min=1, message=u"댓글 내용을 입력해주세요.")
    ])
