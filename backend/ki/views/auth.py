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
from ki.utils import  get_memberships_from_feide, get_users_bots, has_school_access, get_admin_memberships_and_bots


# OAuth 2 client setup
client = WebApplicationClient(os.environ.get('FEIDE_CLIENT_ID'))

message_redirect = 'http://localhost:5173/message' if DEBUG else '/message'


def auth_middleware(get_response):
    @ensure_csrf_cookie
    def load_logged_in_user(request):
        request.userinfo = {}

        username = request.session.get('user.username', None)
        is_authenticated = username is not None
        request.userinfo['isAuthenticated'] = is_authenticated
        if not is_authenticated:
            url_name = resolve(request.path_info).url_name
            if (url_name is None):
                return get_response(request)
            elif (
                url_name.split('.')[0] == 'api'
                and url_name not in ['api.user_bots', 'api.app_config']
            ):
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            else:
                return get_response(request)
        else:   
            # get user's bots
            # TODO: author at multiple schools
            role_obj = models.Role.objects.filter(user_id=username).first()
            role = role_obj.role if role_obj else None
            request.userinfo['username'] = username
            request.userinfo['name'] = request.session.get('user.name')
            request.userinfo['has_access'] = False
            if role == 'admin':
                request.userinfo.update(get_admin_memberships_and_bots(username))
                request.userinfo['has_access'] = True
            else:
                feide_memberships = get_memberships_from_feide(request.session.get('user.auth', False))
                if has_school_access(feide_memberships):
                    request.userinfo.update(feide_memberships)
                    request.userinfo['bots'] = get_users_bots(username, feide_memberships)
                    request.userinfo['has_access'] = True
                    if role == 'author':
                        request.userinfo['author'] = True
                        request.userinfo['auth_school'] = role_obj.school

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
    request.userinfo['username'] = None
    request.userinfo['name'] = None
    request.userinfo['bots'] = []
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
