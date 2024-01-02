from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect
import os
import requests
from app.settings import DEBUG
from .. import models

# TODO: Move all the error handling
# TODO: Add+test retry logic

# Main:
def index(request):
    if request.method == 'POST':
        bot_nr = int(request.POST.get('delete_bot_nr'))
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
            if not request.g.get('admin', False) and not bot.owner == request.g['username']:
                return HttpResponseForbidden()
            bot.delete()

            if bot_nr in request.g.get('bots', []):
                request.g['bots'].remove(bot_nr)
                request.session['user.bots'] = request.g['bots']
        except models.Bot.DoesNotExist:
            # return HttpResponseNotFound()
            redirect('main.index')

    bots = models.Bot.objects.all()
    if request.g.get('logged_on', False):
        users_bots = [bot for bot in bots if bot.bot_nr in request.g.get('bots', [])]
    else:
        users_bots = []

    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "debug": DEBUG,
        "bots": users_bots,
        "page": "index"
    }
    return render(request, 'ki/index.html', context)


def bot(request, bot_nr):
    try:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        # return HttpResponseNotFound()
        return redirect("main.index")
    
    if not int(bot_nr) in request.g.get('bots', []):
        return redirect('main.index')
    
    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "bot_nr": bot_nr,
        "bot": bot,
        "debug": DEBUG,
    }
    return render(request, "ki/bot.html", context)


def adminbot(request, bot_nr):
    def get_groups():
        subjects = []
        # access_list = [subj.subject_id for subj in bot.subjects]
        access_token = request.session.get('user.auth')['access_token']
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

    if not request.g.get('employee', False) and not request.g.get('admin', False):
        return HttpResponseForbidden()

    if bot_nr == 'new':
        bot = models.Bot()
        if not request.g.get('admin', False):
            bot.owner = request.g.get('username')
    else:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
        if not bot:
            return HttpResponseNotFound()

    if request.method == 'POST':
        if bot.owner == request.g.get('username') or request.g.get('admin'):
            bot.title = request.POST.get('title')
            bot.ingress = request.POST.get('ingress')
            bot.prompt = request.POST.get('prompt')
            if request.g.get('admin', False):
                bot.model = request.POST.get('model') or 'gpt-35-turbo-16k'
            else:
                bot.model = 'gpt-35-turbo-16k'
            bot.save()
            bot.bot_nr = bot.pk

        if bot_nr == 'new':
            request.g['bots'].append(bot.bot_nr)
            request.session['user.bots'] = request.g['bots']

        if request.g.get('admin', False):
            acc_dict = {}
            acc_req = request.POST.getlist('access')
            for request_line in acc_req:
                field, access_id, value = request_line.split(':', 3)
                if access_id not in acc_dict:
                    acc_dict[access_id] = {field: value}
                else:
                    acc_dict[access_id].update({field: value})
            for access_id, values in acc_dict.items():
                print("access_id", access_id)
                print("values['s']", values['s'])
                if access_id == 'new' and (values['s'] != '-'):
                    bot_access = models.BotAccess()
                    bot_access.bot_nr_id = bot.pk
                else:
                    try:
                        bot_access = models.BotAccess.objects.get(access_id=access_id)
                    except ValueError:
                        bot_access = None

                if bot_access:
                    if values['s'] == 'del':
                        bot_access.delete()
                    else:
                        bot_access.school_id_id = values['s']
                        bot_access.level = values['l']
                        bot_access.save()

        elif request.g['settings']['allow_groups'] and request.g['dist_to_groups']:
            acc_dict = {}
            acc_req = request.POST.getlist('access')
            if bot_nr == 'new':
                for subject_id in acc_req:
                    acl = models.SubjectAccess(bot_nr=bot, subject_id=subject_id)
                    acl.save()
            else:
                acls_to_remove = list(bot.subjects.all())
                for subject_id in acc_req:
                    if acl := models.SubjectAccess.objects.filter(bot_nr=bot_nr, subject_id=subject_id).first():
                        acls_to_remove.remove(acl)
                    else:
                        acl = models.SubjectAccess(bot_nr=bot, subject_id=subject_id)
                        acl.save()
                for acl in acls_to_remove:
                    acl.delete()

        return redirect('main.index')

    if request.g.get('admin', False):
        schools = models.School.objects.all()
        context = {
            "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
            "bot_nr": bot_nr,
            "bot": bot,
            "schools": schools
        }
    else:
        access_list = [subj.subject_id for subj in bot.subjects.all()] if bot.pk else []
        groups = get_groups()
        groups = [dict(group, checked=group.get('id') in access_list) for group in groups]
        context = {
            "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
            "bot_nr": bot_nr,
            "bot": bot,
            "groups": groups,
            "lifespan": models.Setting.objects.get(setting_key='lifespan').int_val
        }

    return render(request, "ki/adminbot.html", context)


def settings(request):
    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    settings = models.Setting.objects.all()
    schools = models.School.objects.all()
    schools_list = [] 
    if request.method == 'POST':
        if request.POST.get('save_settings') == 'ok':
            for setting in settings:
                if setting_key := request.POST.get(setting.setting_key):
                    if setting.is_txt:
                        setting.txt_val = setting_key
                    else:
                        setting.int_val = int(setting_key)
                    setting.save()
        for school in schools:
            if acc_key := request.POST.get('acc_' + school.org_nr):
                school.access = acc_key
                school.save()
            
            if school.access == 'levels':
                acc_to_remove = list(school.school_accesses.all())
                for level in request.POST.getlist('lev_' + school.org_nr):
                    try:
                        acc = school.school_accesses.get(level=level)
                        acc_to_remove.remove(acc)
                    except models.SchoolAccess.DoesNotExist:
                        acc = models.SchoolAccess(school_id=school, level=level)
                        acc.save()
                ids_to_remove = [acc.access_id for acc in acc_to_remove]
                school.school_accesses.filter(access_id__in=ids_to_remove).delete()

        return redirect('main.settings')

    levels = { 
        "aarstrinn1": "1. trinn", 
        "aarstrinn2": "2. trinn", 
        "aarstrinn3": "3. trinn", 
        "aarstrinn4": "4. trinn", 
        "aarstrinn5": "5. trinn", 
        "aarstrinn6": "6. trinn", 
        "aarstrinn7": "7. trinn", 
        "aarstrinn8": "8. trinn", 
        "aarstrinn9": "9. trinn", 
        "aarstrinn10": "10. trinn", 
        "vg1": "1. vgs", 
        "vg2": "2. vgs", 
        "vg3": "3. vgs"
    }
    for school in schools:
        level_list = []
        for level_code, level_text in levels.items():
            selected = ''
            if school.access == 'levels':
                if level_code in [acc.level for acc in school.school_accesses.all()]:
                    selected = 'selected'
            level_dict = {
                "code": level_code,
                "text": level_text,
                "selected": selected,
            }
            level_list.append(level_dict)

        school_dict = {
            "org_nr":  school.org_nr,
            "school_name":  school.school_name,
            "school_code":  school.school_code,
            "access":  school.access,
            "levels": level_list,
        }
        schools_list.append(school_dict)

    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "settings": settings,
        "schools": schools_list,
        "debug": DEBUG,
    }

    return render(request, 'ki/settings.html', context)


def info(request, page):
    if page == "how_to" and not request.g.get('employee', False):
        return HttpResponseNotFound()
    try:
        text_line = models.PageText.objects.get(page_id=page)
    except models.PageText.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'POST':
        if not request.g.get('admin', False):
            return HttpResponseForbidden()
        content_text = request.POST.get('page_text')
        text_line.page_text = content_text
        text_line.save()

    context = {
        "sitename": os.environ.get('SITENAME', 'KI for Osloskolen'),
        "page": page,
        "content_text": text_line.page_text
    }
    return render(request, "ki/info.html", context)
