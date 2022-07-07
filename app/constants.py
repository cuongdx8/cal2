class Constants:

    ACCESS_ROLE_OWNER = 'owner'
    APP_HOST = 'http://localhost:5000'
    EXPIRED_DAY_NUMBER = 1
    EXPIRED_HOURS_NUMBER = 24

    # Profile
    PROFILE_DEFAULT_FIRST_DAY_OF_WEEK = 'SU'
    PROFILE_DEFAULT_TIMEFORMAT = 'HH'
    PROFILE_DEFAULT_TIMEZONE = 'UTC'
    PROFILE_DEFAULT_LANGUAGE = 'EN'
    PROFILE_DEFAULT_DESCRIPTION = ''
    PROFILE_DEFAULT_AVATAR = 'Avatar'

    # HTTP method
    DELETE_METHOD = 'DELETE'
    PATCH_METHOD = 'PATCH'
    GET_METHOD = 'GET'
    POST_METHOD = 'POST'
    PUT_METHOD = 'UPDATE'

    CONTENT_TYPE_JSON = 'application/json'

    GOOGLE_OAUTH2_API_URL = f'https://www.googleapis.com/oauth2/v2/'
    GOOGLE_AUTHORIZATION_SERVER_URL = 'https://oauth2.googleapis.com/'
    GOOGLE_CALENDAR_API_URL = 'https://www.googleapis.com/calendar/v3/'
    GOOGLE_CREATE_CALENDAR_API_URL = 'https://www.googleapis.com/calendar/v3/calendars'
    GOOGLE_UPDATE_PATCH_DELETE_CALENDAR_API_URL = 'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}'
    GOOGLE_CREATE_EVENT_URL = 'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events'
    GOOGLE_RUD_EVENT_URL = 'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}'
    GOOGLE_MAX_RESULT_RESPONSE = 50



    # Account
    ACCOUNT_TYPE_LOCAL = 'LOCAL'
    ACCOUNT_TYPE_GOOGLE = 'GOOGLE'
    ACCOUNT_TYPE_FACEBOOK = 'FACEBOOK'
    ACCOUNT_TYPE_MICROSOFT = 'MICROSOFT'

    ACCESS_ROLE_DELETED = 'DELETE'

    REGEX_PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

    MIC_CALENDARS_URI = 'https://graph.microsoft.com/v1.0/me/calendars'
    MIC_PROFILE_URI = 'https://graph.microsoft.com/v1.0/users'
    MIC_GET_POST_EVENTS_BY_CALENDAR_URI = 'https://graph.microsoft.com/v1.0/me/calendars/{}/events'

    ACCESS_ROLE_READ = 'READ'
    ACCESS_ROLE_WRITE = 'WRITE'
    ACCESS_ROLE_SHARE = 'SHARE'
    ACCESS_ROLE_FREE_BUSY = 'FREE/BUSY'
    ACCESS_ROLE_FULL = 'READWRITESHARE'

    CREATE_SCHEDULE_FIELDS_REQUIRED = 'name', 'timezone', 'time_by_week_days'
