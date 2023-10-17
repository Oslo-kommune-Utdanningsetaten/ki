from flask import render_template, request, url_for, redirect, Blueprint, session, g, flash, abort, current_app
import openai
import requests 
from app import db
from app.main import models

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        bot_nr = int(request.form.get('delete_bot_nr'))
        bot = models.Bot.query.get(bot_nr)
        if not bot:
            abort(404)
        if not g.admin and not bot.owner == g.username:
            abort(403)
        db.session.delete(bot)
        db.session.commit()

        if bot_nr in g.bots:
            g.bots.remove(bot_nr)
            session['user.bots'] = g.bots

    bots = models.Bot.query.all()
    if g.logged_on:
        users_bots = [bot for bot in bots if bot.bot_nr in g.bots]
    else:
        users_bots = []

    return render_template('index.html', bots=users_bots, page='index')


@main.route('/info/<page>', methods=['GET', 'POST'])
def info(page):
    if page == 'how_to' and not g.employee:
        abort(404)
    text_line = models.PageText.query.get(page)
    
    if request.method == 'POST':
        if not g.admin:
            abort(403)
        content_text = request.form.get('page_text')
        text_line.page_text = content_text
        db.session.add(text_line)
        db.session.commit()

    return render_template('info.html', page=page, content_text=text_line.page_text)


@main.route('/bot/<bot_nr>')
def bot(bot_nr):

    bot = models.Bot.query.get(bot_nr)
    if not bot:
        abort(404)
    if not int(bot_nr) in g.bots:
        return redirect(url_for('main.index'))

    return render_template('bot.html', bot_nr=bot_nr, page='bot')


@main.route('/adminbot/<bot_nr>', methods=['GET', 'POST'])
def adminbot(bot_nr):

    def get_groups():
        subjects = []
        # access_list = [subj.subject_id for subj in bot.subjects]
        access_token = session.get('user.auth')['access_token']
        groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
            }
        try:
            groupinfo_response = requests.get(groupinfo_endpoint, headers=headers)
        except requests.exceptions.ConnectionError as e:
            return []
        else:
            if groupinfo_response.status_code == 200:

                for group in groupinfo_response.json():
                    if group.get('type') == "fc:gogroup":
                        subjects.append({
                            'id': group.get('id'),
                            'display_name': group.get('displayName'),
                            'go_type': group.get('go_type'),
                            # 'checked': group.get('id') in access_list,
                            })
            return subjects

    if not g.employee and not g.admin:
        abort(403)

    if bot_nr == 'new':
        bot = models.Bot()
        if not g.admin:
            bot.owner = g.username

    else:
        bot = models.Bot.query.get(bot_nr)
        if not bot:
            abort(404)

    if request.method == 'POST':
        if bot.owner == g.username or g.admin:
            bot.title = request.form.get('title')
            bot.ingress = request.form.get('ingress')
            bot.prompt = request.form.get('prompt')
            bot.model = request.form.get('model') or 'gpt-3.5-turbo'
            db.session.add(bot)
            db.session.commit()

        if bot_nr == 'new':
            g.bots.append(bot.bot_nr)
            session['user.bots'] = g.bots

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

        elif g.settings['allow_groups']:
            acc_dict = {}
            acc_req = request.form.getlist('access')
            if bot_nr == 'new':
                for subject_id in acc_req:
                    acl = models.SubjectAccess(bot_nr=bot.bot_nr, subject_id=subject_id)
                    db.session.add(acl)
            else:
                acls_to_remove = list(bot.subjects)
                for subject_id in acc_req:
                    if acl := models.SubjectAccess.query.filter_by(bot_nr=bot_nr, subject_id=subject_id).first():
                        acls_to_remove.remove(acl)
                    else:
                        acl = models.SubjectAccess(bot_nr=bot_nr, subject_id=subject_id)
                        db.session.add(acl)
                for acl in acls_to_remove:
                    db.session.delete(acl)

        db.session.commit()
        return redirect(url_for('main.index'))

    if g.admin:
        schools = models.School.query.all()
        return render_template('adminbot.html', bot=bot, schools=schools, page='adminbot')
    else:
        access_list = [subj.subject_id for subj in bot.subjects]
        groups = get_groups()
        groups = [dict(group, checked=group.get('id') in access_list) for group in groups]
        return render_template('adminbot.html', bot=bot, groups=groups, page='adminbot')


@main.route("/settings", methods=['GET','POST'])
def settings():
    if not g.admin:
        abort(403)

    settings = models.Setting.query.all()
    if request.method == 'POST':
        if request.form.get('save_settings') == 'ok':
            for setting in settings:
                if request.form.get(setting.setting_key):
                    if setting.is_txt:
                        setting.txt_val = request.form.get(setting.setting_key)
                    else:
                        setting.int_val = int(request.form.get(setting.setting_key))
                    db.session.add(setting)
        db.session.commit()
        return redirect(url_for('main.settings'))

    return render_template('settings.html', 
                            settings = settings,
                            page = 'settings'
                            )
