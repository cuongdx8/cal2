import json
import re
from typing import Iterable, List

import arrow
import pytz

from app.constants import Constants
from app.exception import ValidateError


def validate_required_field(body, *args):
    if not set(args).issubset(set(body.keys())):
        raise ValidateError('Not found required fields: {}'.format(args))


def validate_can_only_contain_alpha_character(name, value: str):
    value = value.replace(' ', '')
    if not value.isalpha():
        raise ValidateError('{} can only contain alpha characters and spaces'.format(name))


def validate_time_by_week_days(data: dict):
    days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    if not set(days_of_week).issubset(set(data.keys())):
        raise ValidateError('Must contain sunday to saturday')
    for day in days_of_week:
        if isinstance(data.get(day), List):
            for item in data.get(day):
                start = arrow.get(item.get('start'), 'HH:mm:ss')
                end = arrow.get(item.get('end'), 'HH:mm:ss')
                if end.timestamp() < start.timestamp():
                    raise ValidateError('Unavailable value')
        elif 'unavailable'.__eq__(data.get(day)):
            pass
        else:
            raise ValidateError('Unavailable value')


def validate_timezone(timezone: str):
    if timezone in pytz.all_timezones:
        pass
    else:
        raise ValueError('Invalid timezone string!')


def naming_convention(name):
    if re.fullmatch(re.compile(Constants.REGEX_NAMING_CONVENTION), name):
        pass
    else:
        raise ValidateError('Incorrect naming convention.')


def username_convention(name):
    if re.fullmatch(re.compile(Constants.REGEX_USERNAME_CONVENTION), name):
        pass
    else:
        raise ValidateError('Incorrect naming convention.')


def email(email_value):
    if re.fullmatch(re.compile(Constants.REGEX_EMAIL), email_value):
        pass
    else:
        raise ValidateError('Incorrect email.')


def password(password_value):
    if re.fullmatch(re.compile(Constants.REGEX_PASSWORD), password_value):
        pass
    else:
        raise ValidateError('At least 8 characters (required for your Muhlenberg password)—the more characters, '
                            'the better\n'
                            'A mixture of both uppercase and lowercase letters\n'
                            'A mixture of letters and numbers\n'
                            'Inclusion of at least one special character, e.g., ! @ # ? ]')


def validate_alarms(alarms):
    alarms = json.loads(json.dumps(alarms))
    for item in alarms:
        if item.get('method') not in ['email', 'popup']:
            raise ValidateError('Alarms\'s method is invalid. Only email or popup')
        if 40320 < item.get('minutes') < 0:
            raise ValidateError('Alarm\'s minutes is invalid. Must 0 < minutes < 40320')
