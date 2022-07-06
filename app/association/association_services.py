from app.association import ConnectionCalendar
from app.calendar.calendar import Calendar
from app.connection.connection import Connection
from app.constants import Constants


def create_connection_calendar(connection: Connection, calendar: Calendar, access_role: str = Constants.ACCESS_ROLE_READ, default_flag: bool = False, owner_flag: bool = False):
    return ConnectionCalendar(connection_id=connection.id,
                              calendar_id=calendar.id,
                              access_role=access_role,
                              default_flag=default_flag,
                              owner_flag=owner_flag,
                              connection=connection,
                              calendar=calendar)