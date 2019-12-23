from datetime import datetime


_USER_DATE_FORMAT = '%a, %b %d, %Y'  # Thu, Dec 12, 2019
_USER_TIME_FORMAT = '%I:%M %p' # 6:42 AM
_SETTINGS_FILE_DATE_FORMAT = '%Y-%m-%d' # 2019-10-30

def user_date_format(dt):
    # remove any leading pad 0's from date
    return dt.strftime(_USER_DATE_FORMAT).lstrip("0").replace(" 0", " ")

def user_time_format(dt):
    # remove any leading pad 0's from time (except after :'s)
    return dt.strftime(_USER_TIME_FORMAT).lstrip("0").replace(" 0", " ")

def parse_settings_date_time(date_time):
    return datetime.strptime(date_time, _SETTINGS_FILE_DATE_FORMAT)