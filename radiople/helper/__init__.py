# -*- coding: utf-8 -*-

from urllib.parse import urlparse


def append_size(image_url, width, height):
    r = urlparse(image_url)
    return '%s://%s:%d/%dx%d%s' % (r.scheme, r.hostname, r.port, width, height, r.path)
