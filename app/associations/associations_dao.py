from sqlalchemy.orm import Session

from app.associations import ConnectionCalendar, CalendarEvent
from app.calendars.calendars import Calendar
from app.connections.connections import Connection


def create_connection_calendar(connection: Connection, item: ConnectionCalendar, session: Session):
    sql = f'INSERT INTO connection_calendar (connection_id, calendar_id, access_role, default_flag, owner_flag) ' \
          f'VALUES ({connection.id}, {item.calendar.id}, {item.access_role}, {item.default_flag}, {item.owner_flag})'
    session.execute(sql)


def create_calendar_event(calendar: Calendar, item: CalendarEvent, session: Session):
    sql = f'INSERT INTO calendar_event (calendar_id, event_id, owner_flag, response_status) VALUES ' \
          f'({calendar.id}, {item.event.id}, {item.owner_flag}, {item.response_status}'
    session.execute(sql)
