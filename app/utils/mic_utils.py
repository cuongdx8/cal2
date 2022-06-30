import json
import os
import urllib.parse

import requests

from app.connection.connection import Connection
from app.constants import Constants
from app.exception import MicrosoftRequestError

mic_tenant_id = os.environ['MIC-DIRECTORY-ID']
mic_client_id = os.environ['MIC-CLIENT-ID']
mic_redirect_uri = os.environ['MIC-REDIRECT-URL']
mic_scopes = 'User.Read Calendars.ReadWrite offline_access'
mic_client_secret = os.environ['MIC-SECRET-VALUE']


def generate_url_login(state):
    params = {
        'client_id': mic_client_id,
        'response_type': 'code',
        'redirect_uri': mic_redirect_uri,
        'response_mode': 'query',
        'scope': mic_scopes,
        'state': state
    }
    return f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/authorize?' \
           f'{urllib.parse.urlencode(params)}'


def request_exchange_code(code):
    params = {
        'client_id': mic_client_id,
        'scope': mic_scopes,
        'code': code,
        'redirect_uri': mic_redirect_uri,
        'grant_type': 'authorization_code',
        'client_secret': mic_client_secret
    }

    response = requests.post(url=f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/token', data=params)
    return json.loads(response.text)


def refresh_token(credentials: dict):
    params = {
        'client_id': mic_client_id,
        'scope': mic_scopes,
        'refresh_token': credentials.get('refresh_token'),
        'redirect_uri': mic_redirect_uri,
        'grant_type': 'refresh_token',
        'client_secret': mic_client_secret
    }
    res = requests.post(url=f'https://login.microsoftonline.com/{mic_tenant_id}/oauth2/v2.0/token', data=params)
    return json.loads(res.text)


def create_authorized_request(url: str, connection: Connection, method: str, deep=0, **kwargs) -> dict:
    credentials = connection.credentials
    headers = {"Authorization": f"Bearer {credentials.get('access_token')}",
               "Content-Type": "application/json"}
    match method:
        case Constants.POST_METHOD:
            res = requests.post(url, headers=headers, **kwargs)
        case Constants.GET_METHOD:
            res = requests.get(url, headers=headers, **kwargs)
        case Constants.PATCH_METHOD:
            res = requests.patch(url=url, headers=headers, **kwargs)
        case Constants.DELETE_METHOD:
            res = requests.delete(url=url, headers=headers, **kwargs)
        case _:
            raise ValueError(f'Method = {method} is invalid')
    if res.status_code == 401 and deep < 1:
        connection.credentials = refresh_token(credentials=connection.credentials)
        res = create_authorized_request(url, connection, method=method, deep=1, **kwargs)
    if 200 <= res.status_code < 300:
        return json.loads(res.text)
    else:
        raise MicrosoftRequestError(message=res.text)


def get_profile(credentials):
    response = create_authorized_request(Constants.MIC_PROFILE_URI, connection=Connection(credentials=credentials),
                                         method=Constants.GET_METHOD)
    return response.get('value')[0]
