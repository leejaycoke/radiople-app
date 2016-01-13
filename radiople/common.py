# -*- coding: utf-8 -*-

import pytz
from datetime import datetime

KST_TIME_ZONE = pytz.timezone('Asia/Seoul')


def kst_now():
    return datetime.now(KST_TIME_ZONE)
