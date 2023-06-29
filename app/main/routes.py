from flask import render_template, request, url_for, redirect, Blueprint, session, g, flash, abort, current_app
import openai
from app.main import models

main = Blueprint('main', __name__)

@main.route('/')
def index():
    bots = models.BotInfo.query.all()
    if g.logged_on:
        users_bots = [bot for bot in bots if bot.bot_nr in g.bots]
    else:
        users_bots = []

    return render_template('index.html', bots=users_bots)


@main.route('/bot/<bot_nr>')
def bot(bot_nr):

    bot_info = models.BotInfo.query.get(bot_nr)
    if not bot_info:
        abort(404)
    if not int(bot_nr) in g.bots:
        return redirect(url_for('main.index'))

    return render_template('bot.html', bot_nr=bot_nr)



