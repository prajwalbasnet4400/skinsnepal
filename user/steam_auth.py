from django.http import HttpResponse
from django.conf import settings
from urllib.parse import urlencode
import re
import requests
from urllib.parse import urlencode
from django.urls import reverse
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()

# TODO: Make this dynamic
STEAM_LOGIN_URL = 'https://steamcommunity.com/openid/login'
STEAM_AUTH_REALM = 'http://127.0.0.1:8000'
ABSOLUTE_URL = getattr(settings, 'ABSOLUTE_URL', 'localhost:8000')
STEAM_LOGIN_URL = 'https://steamcommunity.com/openid/login'


def auth():
    STEAM_AUTH_CALLBACK_URL = f"http://127.0.0.1:8000{reverse('api:user:steam_callback')}"

    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': STEAM_AUTH_CALLBACK_URL,
        'openid.realm': STEAM_AUTH_REALM,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }

    response = HttpResponse()
    response['Location'] = f'{STEAM_LOGIN_URL}?{urlencode(params)}'
    response['Content-Type'] = 'application/x-www-form-urlencoded'
    response.status_code = 302
    return response


def get_uid(results):
    results = dict(results)

    args = {
        'openid.assoc_handle': results['openid.assoc_handle'][0],
        'openid.signed': results['openid.signed'][0],
        'openid.sig': results['openid.sig'][0],
        'openid.ns': results['openid.ns'][0]
    }

    signed_args = results['openid.signed'][0].split(',')

    for arg in signed_args:
        arg = 'openid.{0}'.format(arg)
        if results[arg][0] not in args:
            args[arg] = results[arg][0]

    args['openid.mode'] = 'check_authentication'

    response = requests.post(STEAM_LOGIN_URL, args)

    if re.search(r'is_valid:true', response.text):
        matches = re.search(
            r'https://steamcommunity.com/openid/id/(\d+)', results['openid.claimed_id'][0])
        if matches is not None and matches.group(1) is not None:
            return matches.group(1)
        else:
            return None
    else:
        return None


def associate_user(uid):
    """
        Takes player dict as arg
    """

    response = requests.get(
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/', params={
            'key': settings.STEAM_API_KEY, 'steamids': uid})
    player = response.json().get('response').get('players')[0]
    user = USER_MODEL.objects.filter(steamid64=player.get('steamid'))
    if not user.exists():
        user = USER_MODEL.objects.create(username=player.get('personaname'), steamid64=player.get(
            'steamid'), first_name=player.get('realname'), avatar=player.get('avatarfull'))
    else:
        user = user.first()
    return user
