from dateutil.parser import parse

def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def to_date(string, fuzzy=False):
    try:
        return parse(string, fuzzy=fuzzy)
    except ValueError:
        return ""