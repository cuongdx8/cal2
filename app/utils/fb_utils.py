import os
import urllib.parse

import requests

fb_client_id = os.environ['FB-CLIENT-ID']
fb_client_secret = os.environ['FB-CLIENT-SECRET']
fb_redirect_uri = os.environ['FB-REDIRECT-URI']
fb_scopes = 'public_profile'


def generate_url_login(state):
    params = {
        'client_id': fb_client_id,
        'redirect_uri': fb_redirect_uri
    }
    if state is not None:
        params.update({'state': state})

    params_encode = urllib.parse.urlencode(params)
    return f'https://www.facebook.com/v13.0/dialog/oauth?{params_encode}'


def request_exchange_code(code: str):
    params = {
        'client_id': fb_client_id,
        'redirect_uri': fb_redirect_uri,
        'client_secret': fb_client_secret,
        'code': code
    }
    params_encoded = urllib.parse.urlencode(params)
    res = requests.get(f'https://graph.facebook.com/v13.0/oauth/access_token?{params_encoded}')
    return res.text


def get_user_info(access_token):
    params = {
        'access_token': access_token
    }
    params_encoded = urllib.parse.urlencode(params)
    return requests.get(f'https://graph.facebook.com/me?{params_encoded}').text