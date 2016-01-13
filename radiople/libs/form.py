# -*- coding: utf-8 -*-

from wtforms import Form


class BaseForm(Form):

    @property
    def error_message(self):
        if self.errors:
            message = next(iter(self.errors.values()))[0]
            return message[0] if isinstance(message, list) else message

    def get_error_message(self):
        if self.errors:
            for v in self.errors.values():
                return v[0]
        return ""

    def get_error_messages(self, delimiter='\n'):
        messages = []
        if self.errors:
            messages = [v[0] for v in self.errors.values()]

        if delimiter:
            return delimiter.join(messages)
        return messages
