from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.event.event import Event


def create_calendar(calendar: Calendar, connection: Connection) -> Calendar:
    return calendar


def update_calendar(calendar: Calendar, connection: Connection) -> Calendar:
    return calendar


def delete_calendar(calendar_id, connection):
    pass


def patch_calendar(calendar: Calendar, new_calendar: Calendar, connection: Connection) -> Calendar:
    return new_calendar


def create_event(event: Event, calendar: Calendar, connection: Connection):
    return event
