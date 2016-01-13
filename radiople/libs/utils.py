import pytz
from datetime import datetime

ASIA_SEOUL = pytz.timezone('Asia/Seoul')


def now():
    return datetime.now(ASIA_SEOUL)
