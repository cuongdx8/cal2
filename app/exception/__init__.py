from typing import List


class UserExistsInDatabase(Exception):

    def __init__(self):
        self.message = 'User exists in database'

    def __str__(self):
        return f'{self.message}'


class NotFoundRequiredData(Exception):
    def __init__(self, *args):
        self.message = '{} is required'.format(args)

    def __str__(self):
        return f'{self.message}'


class NotFoundUser(Exception):
    pass


class JWTError(Exception):
    pass


class UserNameOrPasswordInvalid(Exception):
    pass


class MicrosoftRequestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class ValidateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class TryDeletePrimaryCalendarGoogleException(Exception):
    pass
