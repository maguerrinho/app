import re


def format_phone(phone):
    if phone is None:
        return ''
    if isinstance(phone, int):
        phone = str(phone)
    return re.sub(r'\D', '', phone)
