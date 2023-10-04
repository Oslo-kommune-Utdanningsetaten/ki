from flask import render_template, request, url_for, redirect, Blueprint, session, g, flash, abort, current_app
import openai
import requests 
from app import db
from app.main import models

main = Blueprint('main', __name__)

@main.route('/')
def index():
    bots = models.Bot.query.all()

    if g.logged_on:
        users_bots = [bot for bot in bots if bot.bot_nr in g.bots]
    elif g.admin:
        users_bots = bots
    else:
        users_bots = []

    return render_template('index.html', bots=users_bots)


@main.route('/bot/<bot_nr>')
def bot(bot_nr):

    bot = models.Bot.query.get(bot_nr)
    if not bot:
        abort(404)
    if not int(bot_nr) in g.bots:
        return redirect(url_for('main.index'))

    return render_template('bot.html', bot_nr=bot_nr)


@main.route('/adminbot/<bot_nr>', methods=['GET','POST'])
def adminbot(bot_nr):

    bot = models.Bot.query.get(bot_nr)
    teacher = bot.owner == g.username

    if not bot:
        abort(404)
    if not teacher and not g.admin:
        abort(403)

    def get_groups():
        subjects = []
        access_list = [subj.subject_id for subj in bot.subjects]
        access_token = session.get('user.auth')['access_token']
        groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
            }
        try:
            groupinfo_response = requests.get(groupinfo_endpoint, headers=headers)
        except requests.exceptions.ConnectionError as e:
            return None
        else:
            if groupinfo_response.status_code == 200:

                for group in groupinfo_response.json():
                    if group.get('type') == "fc:gogroup":
                        subjects.append({
                            'id': group.get('id'),
                            'display_name': group.get('displayName'),
                            'go_type': group.get('go_type'),
                            'checked': group.get('id') in access_list,
                            })
                return subjects

    if request.method == 'POST':
        # accesses = bot.accesses
        bot.title = request.form.get('title')
        bot.ingress = request.form.get('ingress')
        bot.prompt = request.form.get('prompt')
        bot.model = request.form.get('model') or 'gpt-3.5-turbo'

        if g.admin:
            acc_dict = {}
            acc_req = request.form.getlist('access')
            for request_line in acc_req:
                field, access_id, value = request_line.split(':', 3)
                if access_id not in acc_dict:
                    acc_dict[access_id] = {field: value}
                else:
                    acc_dict[access_id].update({field: value})
            for access_id, values in acc_dict.items():
                if access_id == 'new' and (values['s'] != '-'):
                    bot_access = models.BotAccess()
                    bot_access.bot_nr = bot_nr
                else:
                    bot_access = models.BotAccess.query.get(access_id)

                if bot_access:
                    if values['s'] == 'del':
                        db.session.delete(bot_access)
                    else:
                        bot_access.school_id = values['s']
                        bot_access.level = values['l']
                        db.session.add(bot_access)

        elif teacher:
            acc_dict = {}
            acc_req = request.form.getlist('access')
            acls_to_remove = list(bot.subjects)
            for subject_id in acc_req:
                if acl := models.SubjectAccess.query.filter_by(bot_nr=bot_nr, subject_id=subject_id).first():
                    acls_to_remove.remove(acl)
                else:
                    acl = models.SubjectAccess(bot_nr=bot_nr, subject_id=subject_id)
                    db.session.add(acl)
            for acl in acls_to_remove:
                db.session.delete(acl)

        db.session.add(bot)
        db.session.commit()

    if g.admin:
        schools = models.School.query.all()
        return render_template('adminbot.html', bot=bot, schools=schools)
    elif teacher:
        groups = get_groups()
        return render_template('adminbot.html', bot=bot, groups=groups)


