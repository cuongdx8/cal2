import datetime

from app.calendars.calendars import Calendar
from app.constants import Constants


def init_calendar():
    calendar = Calendar()
    calendar.type = Constants.ACCOUNT_TYPE_LOCAL
    calendar.color_id = Constants.DEFAULT_COLOR_ID
    calendar.timezone = Constants.DEFAULT_TIMEZONE
    calendar.default_reminders = Constants.DEFAULT_REMINDER
    calendar.created_at = calendar.updated_at = datetime.datetime.utcnow()
    return calendar
