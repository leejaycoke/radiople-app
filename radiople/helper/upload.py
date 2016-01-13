# -*- coding: utf-8 -*-


def get_extension(filename, with_dot=False):
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return '.%s' % extension if with_dot else extension
