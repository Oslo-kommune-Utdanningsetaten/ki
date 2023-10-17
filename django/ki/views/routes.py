from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
import os
from app.settings import DEBUG
from .. import models

# TODO: Move all the error handling
# TODO: Add+test retry logic

# Main:
def index(request):
    bots = models.Bot.objects.all()
    if request.g.get('logged_on', False):
        users_bots = [bot for bot in bots if bot.bot_nr in request.g.get('bots', [])]
    else:
        users_bots = []

    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "debug": DEBUG,
        "bots": users_bots
    }
    return render(request, 'ki/index.html', context)


def bot(request, bot_nr):
    try:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()
    
    if not int(bot_nr) in request.g.get('bots', []):
        return redirect('main.index')
    
    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "bot_nr": bot_nr,
        "bot": bot
    }
    return render(request, "ki/bot.html", context)


def adminbot(request, bot_nr):
    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "bot_nr": bot_nr
    }
    return render(request, "ki/adminbot.html", context)


# WIP:
def wip(request):
    return render(request, "ki/_wip.html")
