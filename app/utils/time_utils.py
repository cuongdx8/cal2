import datetime

from app.constants import Constants


def event_time_to_datetime(str_timme):
    return datetime.datetime.strptime(str_timme, Constants.EVENT_TIME_FORMAT)