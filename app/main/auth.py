from flask import Blueprint, flash, g, redirect, render_template, \
    request, session, url_for, current_app, jsonify, abort
from werkzeug.security import check_password_hash, generate_password_hash
from oauthlib.oauth2 import WebApplicationClient
import requests 
import json
import os
from app import db
from app.main import models

auth = Blueprint('auth', __name__, url_prefix='/auth')

# OAuth 2 client setup
client = WebApplicationClient(current_app.config['FEIDE_CLIENT_ID'])


@auth.before_app_request
def load_logged_in_user():
        username = session.get('user.username')
        g.logged_on = False
        g.admin = False
        if username is None:
            if (request.blueprint in ['main'] and
                    request.path != url_for('main.index')):
                return redirect(url_for('auth.feidelogin'))
            elif request.blueprint in ['api']:
                abort(401) 
        else:
            g.logged_on = True
            g.username = username
            g.name = session.get('user.name')
            g.bots = session.get('user.bots')
            g.token = session.get('user.auth')


            # temp admin access
            if username == "fnygard@feide.osloskolen.no":
                bots = models.Bot.query.all()
                g.bots = [bot.bot_nr for bot in bots]
                g.admin = True

@auth.route('/login', methods=('GET', 'POST'))
def login():

    if not os.environ.get("FLASK_DEBUG", False):
        abort(404)

    # return render_template('login.html')
    return redirect(url_for('main.index'))


def get_provider_cfg():
    return requests.get(current_app.config['FEIDE_DISCOVERY_URL']).json()


@auth.route("/feidelogin")
def feidelogin():
    # Find out what URL to hit for Feide login
    feide_provider_cfg = get_provider_cfg()
    authorization_endpoint = feide_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Feide login and provide
    # scopes that let you retrieve user's profile from Feide
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri = current_app.config['FEIDE_CALLBACK'],
        scope = ["openid", "userid", "profile", "userid-feide", "groups-org", "groups-edu"],
        login_hint = "feide|realm|feide.osloskolen.no",
    )
    return redirect(request_uri)

@auth.route('feidecallback')
def feidecallback():
    # Get authorization code Feide sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    provider_cfg = get_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        redirect_url = current_app.config['FEIDE_CALLBACK'],
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['FEIDE_CLIENT_ID'], current_app.config['FEIDE_CLIENT_SECRET']),
    )

    # Parse the tokens!
    tokens = client.parse_request_body_response(json.dumps(token_response.json()))

    # get the user's profile information
    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    username = userinfo_response.json()["https://n.feide.no/claims/eduPersonPrincipalName"]
    if username:
        access = models.BotAccess.query.all()
        schools = []
        levels = []
        employee = False
        bots = []
        # get user's school info
        groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
        uri, headers, body = client.add_token(groupinfo_endpoint)
        groupinfo_response = requests.get(uri, headers=headers, data=body)
        # print(groupinfo_response.json())

        for group in groupinfo_response.json():
            # role empoyee from parent org
            if (group.get('id') == "fc:org:feide.osloskolen.no" and
                        group['membership']['primaryAffiliation'] == "employee"):
                employee = True
            # school org_nr(s) from child org(s)
            if (group.get('type') == "fc:org" and 
                        group.get("parent") == "fc:org:feide.osloskolen.no"):
                school_id = group['id'].split(":")[4] # fifth part of id is org_nr
                school = models.School.query.get(school_id)
                if school:
                    schools.append(school)
            # level(s) from grep
            if (group.get('type') == "fc:grep" and 
                        group.get('grep_type') == "aarstrinn"):
                levels.append(group['code'])
        for line in access:
            for school in schools:
                if (line.school_id == school.org_nr) or (line.school_id == '*'):
                    if employee or (line.level == '*'):
                        if line.bot_nr not in bots:
                            bots.append(line.bot_nr)
                    else:
                        for level in levels:
                            if line.level == level:
                                if line.bot_nr not in bots:
                                    bots.append(line.bot_nr)

        if bots:
            name = userinfo_response.json()["name"]
            session['user.username'] = username
            session['user.name'] = name
            session['user.bots'] = bots
            session['user.auth'] = tokens['id_token']
        else:
            session.clear()

    else:
        session.clear()

    return redirect(url_for('main.index'))


@auth.route('/logout')
def logout():
    session.clear()
    g.username = None
    g.name = None
    g.bots = []
    if g.logged_on and g.token:
        g.logged_on = False
        feide_provider_cfg = get_provider_cfg()
        end_session_endpoint = feide_provider_cfg["end_session_endpoint"]
        site_url = request.referrer
        return_uri = f"{end_session_endpoint}?post_logout_redirect_uri={site_url}&id_token_hint={g.token}"
        return redirect(return_uri)
    else:
        return redirect(url_for('main.index'))
