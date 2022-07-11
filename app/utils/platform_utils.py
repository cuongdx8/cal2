from typing import Union

from app.users.users import User
from app.calendars.calendars import Calendar
from app.connections.connections import Connection
from app.constants import Constants
from app.events.events import Event
from app.utils import gg_utils, fb_utils, mic_utils, local_utils


def get(instance: Union[Calendar, Connection, User, Event]):
    match instance.type:
        case Constants.ACCOUNT_TYPE_GOOGLE:
            return gg_utils
        case Constants.ACCOUNT_TYPE_MICROSOFT:
            return mic_utils
        case Constants.ACCOUNT_TYPE_FACEBOOK:
            return fb_utils
        case Constants.ACCOUNT_TYPE_LOCAL:
            return local_utils
        case _:
            raise ValueError('Instance\'s type is invalid.')
