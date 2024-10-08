from django.http import HttpResponse, HttpResponseNotFound
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

# OAuth 2 client setup
client = WebApplicationClient(os.environ.get('FEIDE_CLIENT_ID'))

message_redirect = 'http://localhost:5173/message' if DEBUG else '/message'

def get_user_bots(request, username):
    # bot_access = models.BotAccess.objects.all()
    access = False
    schools = []
    levels = []
    groups = []
    dist_to_groups = False
    employee = False
    bots = set()
    allow_groups = bool(models.Setting.objects.get(
        setting_key='allow_groups').int_val)
    allow_personal = bool(models.Setting.objects.get(
        setting_key='allow_personal').int_val)
    lifespan = models.Setting.objects.get(
        setting_key='lifespan').int_val
    if not (tokens := request.session.get('user.auth', False)):
        return [], False, False, []
    # get user's grups from dataporten
    groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
    headers = {"Authorization": "Bearer " + tokens['access_token']}
    groupinfo_response = requests.get(
        groupinfo_endpoint, 
        headers=headers
        )
    if groupinfo_response.status_code == 401:
        request.session.clear()
        return [], False, False, []

    # get user's schools and levels
    for group in groupinfo_response.json():
        # role empoyee from parent org
        if (group.get('id') == "fc:org:feide.osloskolen.no" and
                group['membership']['primaryAffiliation'] == "employee"):
            employee = True
        # school org_nr(s) from child org(s)
        if (group.get('type') == "fc:org" and
                group.get("parent") == "fc:org:feide.osloskolen.no"):
            # fifth part of id is org_nr
            org_nr = group['id'].split(":")[4]
            school = models.School.objects.get(org_nr=org_nr)
            if school:
                schools.append(school)
        # level(s) from grep
        if (group.get('type') == "fc:grep" and
                group.get('grep_type') == "aarstrinn"):
            levels.append(group['code'])
        # education groups
        if (group.get('type') == "fc:gogroup"):
            groups.append(group.get('id'))

    # has user's schools access?
    for school in schools:
        if employee:
            if school.access in ['emp', 'all', 'levels']:
                access = True
                if school.access != 'emp':
                    dist_to_groups = True
        else:
            if school.access == 'all':
                access = True
            elif school.access == 'levels':
                for line in school.school_accesses.all():
                    if line.level in levels:
                        access = True
    if not access:
        return None, False, False, []
    
    # bots from subject
    if allow_groups and not employee:
        for group_id in groups:
            subject_accesses = models.SubjectAccess.objects.filter(
                subject_id=group_id)
            for line in subject_accesses:
                if (line.created and 
                        (line.created.replace(tzinfo=None) + timedelta(hours=lifespan) < datetime.now())):
                    line.delete()
                else:
                    bots.add(line.bot_id_id)

    # bots from school
    for school in schools:
        for bot_access in school.accesses.all():
            access = False
            match bot_access.access:
                case 'all':
                    access = True
                case 'emp':
                    if employee:
                        access = True
                case 'levels':
                    if employee:
                        access = True
                    else:
                        for level in bot_access.levels.all():
                            if level.level in levels:
                                access = True
            if access:
                bots.add(bot_access.bot_id_id)
                                
    # bots from personal
    if allow_personal:
        personal_bots = models.Bot.objects.filter(owner=username)
        for line in personal_bots:
            bots.add(line.uuid)

    return bots, employee, dist_to_groups, schools


def auth_middleware(get_response):
    @ensure_csrf_cookie
    def load_logged_in_user(request):
        request.g = {}
        bots = set()
        admin = False
        has_access = False

        username = request.session.get('user.username', None)
        if username is None:
            has_access = False
            url_name = resolve(request.path_info).url_name
            if (url_name is None):
                response = get_response(request)
                return response
            elif (url_name.split('.')[0] == 'main' and
                    request.path != resolve_url('main.index')):
                return redirect('auth.feidelogin')
        
        # get user's bots
        role_obj = models.Role.objects.filter(user_id=username).first()
        role = role_obj.role if role_obj else None
        if role == 'admin':
            request.g['dist_to_groups'] = False
            admin = True
            has_access = True
            personal_bots = models.Bot.objects.filter(owner=username)
            bots.update((bot.uuid for bot in personal_bots))
            library_bots = models.Bot.objects.filter(library = True)
            bots.update((bot.uuid for bot in library_bots))
        else:
            bots, employee, dist_to_groups, schools = get_user_bots(request, username)
            request.g['employee'] = employee
            request.g['dist_to_groups'] = dist_to_groups
            request.g['schools'] = schools
            if role == 'author':
                request.g['author'] = True
                request.g['auth_school'] = role_obj.school
            if bots is not None:
                has_access = True

        request.g['bots'] = list(bots) if bots else []
        request.g['admin'] = admin
        request.g['has_access'] = has_access
        request.g['username'] = username
        request.g['name'] = request.session.get('user.name')

        # load settings
        settings_dict = {}
        for item in models.Setting.objects.all():
            if item.int_val != None:
                settings_dict[item.setting_key] = item.int_val
            elif item.txt_val != None:
                settings_dict[item.setting_key] = item.txt_val
        request.g['settings'] = settings_dict


        response = get_response(request)
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
    request.g['has_access'] = False
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
