from django.shortcuts import render
import os
from app.settings import DEBUG

# TODO: move g to proper place (request.g set during auth/pre_processor)
g = {
    'employee': False,
    'admin': True,
    'settings': {},
    'logged_on': True,
}

# Main:
def index(request):
    request.g = g
    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "debug": DEBUG,
    }
    return render(request, 'ki/index.html', context)


def bot(request, bot_nr):
    request.g = g
    context = {
        "bot_nr": bot_nr
    }
    return render(request, "ki/bot.html", context)


def adminbot(request, bot_nr):
    request.g = g
    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "bot_nr": bot_nr
    }
    return render(request, "ki/adminbot.html", context)


# WIP:
def wip(request):
    return render(request, "ki/_wip.html")
