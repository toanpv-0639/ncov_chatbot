from dateutil.parser import parse
from dateutil import tz

def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def to_date(string, fuzzy=False):
    try:
        VN_TZ = tz.gettz('Asia/Ho_Chi_Minh')
        UTC = tz.gettz('UTC')
        date = parse(string, fuzzy=fuzzy).replace(tzinfo=UTC)
        return date.astimezone(VN_TZ)
    except ValueError:
        return ""