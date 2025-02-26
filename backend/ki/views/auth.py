from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, resolve_url
from django.urls import resolve
import requests
import json
import os
import urllib.parse
from datetime import datetime, timedelta
from oauthlib.oauth2 import WebApplicationClient
from .. import models
from app.settings import DEBUG
from django.views.decorators.csrf import ensure_csrf_cookie
from ki.utils import load_feide_memberships_to_request, has_school_access, load_users_bots_to_request


# OAuth 2 client setup
client = WebApplicationClient(os.environ.get('FEIDE_CLIENT_ID'))

message_redirect = 'http://localhost:5173/message' if DEBUG else '/message'


def auth_middleware(get_response):
    @ensure_csrf_cookie
    def load_logged_in_user(request):
        request.g = {}
        bots = set()
        is_admin = False

        username = request.session.get('user.username', None)
        is_authenticated = username is not None
        request.g['isAuthenticated'] = is_authenticated
        # load settings
        settings_dict = {}
        all_settings = models.Setting.objects.all()
        for setting in all_settings:
            if setting.int_val != None:
                settings_dict[setting.setting_key] = setting.int_val
            elif setting.txt_val != None:
                settings_dict[setting.setting_key] = setting.txt_val

        request.g['settings'] = settings_dict
        if not is_authenticated:
            url_name = resolve(request.path_info).url_name
            if (url_name is None):
                return get_response(request)
            elif (
                url_name.split('.')[0] == 'api'
                and url_name not in ['api.user_bots', 'api.menu_items']
            ):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            else:
                return get_response(request)
        else:   
            # get user's bots
            # TODO: author at multiple schools
            role_obj = models.Role.objects.filter(user_id=username).first()
            role = role_obj.role if role_obj else None
            if role == 'admin':
                bots:set = set()
                personal_bots = models.Bot.objects.filter(owner=username)
                bots.update((bot.uuid for bot in personal_bots))
                library_bots = models.Bot.objects.filter(library = True)
                bots.update((bot.uuid for bot in library_bots))
                request.g['bots'] = list(bots) if bots else []
                request.g['admin'] = True
                request.g['has_access'] = True
            else:
                load_feide_memberships_to_request(request)
                if has_school_access(request):
                    load_users_bots_to_request(request)
                    request.g['has_access'] = True
                    if role == 'author':
                        request.g['author'] = True
                        request.g['auth_school'] = role_obj.school
                        request.g['admin'] = False
                # TODO: 
                # else:


            request.g['username'] = username
            request.g['name'] = request.session.get('user.name')

        response = get_response(request)
        response['X-Is-Authenticated'] = str(is_authenticated).lower()
        return response   

    return load_logged_in_user


def get_provider_cfg():
    return requests.get(os.environ.get('FEIDE_DISCOVERY_URL')).json()


def feidelogin(request):
    # Find out what URL to hit for Feide login
    feide_provider_cfg = get_provider_cfg()
    authorization_endpoint = feide_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Feide login and provide
    # scopes that let you retrieve user's profile from Feide
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=os.environ.get('FEIDE_CALLBACK'),
        scope=["openid", "userid", "profile",
               "userid-feide", "groups-org", "groups-edu"],
        login_hint="feide|realm|feide.osloskolen.no",
    )
    return redirect(request_uri)


def feidecallback(request):
    # Get authorization code Feide sent back to you
    code = request.GET.get("code", "")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    provider_cfg = get_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        redirect_url=os.environ.get('FEIDE_CALLBACK'),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(os.environ.get('FEIDE_CLIENT_ID'),
              os.environ.get('FEIDE_CLIENT_SECRET')),
    )

    # Parse the tokens!
    tokens = client.parse_request_body_response(
        json.dumps(token_response.json()))
    
    # get the user's profile information
    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    username = userinfo_response.json(
    )["https://n.feide.no/claims/eduPersonPrincipalName"]

    if username:
        request.session['user.auth'] = tokens
        request.session['user.username'] = username
        request.session['user.name'] = userinfo_response.json()["name"]
        return redirect('http://localhost:5173/' if DEBUG else '/')

    else:
        request.session.clear()
        return redirect(f'{message_redirect}/Feide login feilet./error')


def logout(request):
    token = request.session.get('user.auth', False)
    request.session.clear()
    request.g['username'] = None
    request.g['name'] = None
    request.g['bots'] = []
    if token:
        id_token = token['id_token']
        feide_provider_cfg = get_provider_cfg()
        redirect_uri=os.environ.get('FEIDE_LOGOUT_REDIR')
        end_session_endpoint = feide_provider_cfg["end_session_endpoint"]+'?'
        params = {
            "post_logout_redirect_uri": redirect_uri, 
            "id_token_hint": id_token,
        }
        return_uri = end_session_endpoint + urllib.parse.urlencode(params)
        return redirect(return_uri)
    else:
        return redirect('http://localhost:5173/' if DEBUG else '/')


def logged_out(request):
    return redirect(f'{message_redirect}/Du er nå logget ut./info')
