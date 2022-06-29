from sqlalchemy.orm import Session

from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.utils import gg_utils


def load_events_by_calendar(calendar: Calendar, connection: Connection):
    return gg_utils.load_events_by_calendar(calendar, connection)
