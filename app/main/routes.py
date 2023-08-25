from flask import render_template, request, url_for, redirect, Blueprint, session, g, flash, abort, current_app
import openai
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

@main.route('/om')
def om():
    return render_template('om.html')

@main.route('/personvern')
def personvern():
    return render_template('personvern.html')

@main.route('/lerere')
def lerere():
    return render_template('lerere.html')

@main.route('/elever')
def elever():
    return render_template('elever.html')


@main.route('/adminbot/<bot_nr>', methods=['GET','POST'])
def adminbot(bot_nr):

    if not g.admin:
        abort(403)

    bot = models.Bot.query.get(bot_nr)
    if not bot:
        abort(404)
    schools = models.School.query.all()

    if request.method == 'POST':
        # accesses = bot.accesses
        bot.title = request.form.get('title')
        bot.ingress = request.form.get('ingress')
        bot.prompt = request.form.get('prompt')
        bot.model = request.form.get('model')


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



        db.session.add(bot)
        db.session.commit()

    return render_template('adminbot.html', bot=bot, schools=schools)


