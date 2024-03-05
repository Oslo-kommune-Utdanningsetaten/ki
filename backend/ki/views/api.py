from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime, timedelta
import requests
from openai import AsyncAzureOpenAI
import os
import json
# from ..mock import mock_acreate


azureClient = AsyncAzureOpenAI(
    azure_endpoint=os.environ.get('OPENAI_API_BASE'),
    api_key=os.environ.get('OPENAI_API_KEY'),
    api_version=os.environ.get('OPENAI_API_VERSION'),
    )


@api_view(["GET"])
def page_text(request, page):

    try:
        text_line = models.PageText.objects.get(page_id=page)
    except models.PageText.DoesNotExist:
        return Response(status=404)

    if (not request.g.get('employee', False) 
        and not request.g.get('admin', False)
        and not text_line.public):
        return Response(status=403)

    return Response({
        "page": page,
        "content_text": text_line.page_text
    })

@api_view(["GET"])
def menu_items(request):
    menu_items = []
    info_pages = models.PageText.objects.all()
    
    if request.g.get('logged_on', False):
        # menu_items.append({
        #     'title': 'Logg ut',
        #     'url': '/',
        # })
        if request.g.get('admin', False):
            menu_items.append({
                'title': 'Innstillinger',
                'url': '/settings',
            })
        for page in info_pages:
            if page.public or request.g.get('employee', False) or request.g.get('admin', False):
                menu_items.append({
                    'title': page.page_title,
                    'url': f'/info/{page.page_id}',
                })
        menu_items.append({
            'title': 'Startside',
            'url': '/',
        })
    # else:
    #     menu_items.append({
    #         'title': 'Logg inn',
    #         'url': '/auth/feidelogin',
    #     })

    return Response({'menuItems': menu_items}, content_type='application/json')

@api_view(["GET"])
def user_bots(request):
    bots = models.Bot.objects.all()
    if request.g.get('logged_on', False):
        users_bots = [
            {
                'bot_nr': bot.bot_nr,
                'bot_title': bot.title,
                'bot_img': bot.image or "bot5.svg",
            }
            for bot in bots if bot.bot_nr in request.g.get('bots', [])
        ]
        if (request.g.get('admin', False) or 
                request.g.get('employee', False) and 
                models.Setting.objects.get(setting_key='allow_personal')):
            users_bots.append({
                    'bot_nr': 0,
                    'bot_title': "Ny bot",
                    'bot_img': "pluss.svg",
                })
    else:
        users_bots = []

    return Response({'bots': users_bots})


@api_view(["GET", "POST", "PUT", "DELETE"])
def bot_info(request, bot_nr):

    if not bot_nr in request.g.get('bots', []) and bot_nr != 0:
        return Response(status=403)

    # Make new bot on POST
    if request.method == "POST":
        bot = models.Bot()
        if not request.g.get('admin', False):
            bot.owner = request.g.get('username')
        # TODO: remove this?
        request.g['bots'].append(bot.bot_nr)
        request.session['user.bots'] = request.g['bots']
    else:
        if request.method == "GET" and bot_nr == 0:
            return Response({'bot': {
                'bot_nr': 0,
                'title': "",
                'ingress': "",
                'prompt': "",
                'model': models.Setting.objects.get(setting_key='default_model').txt_val,
                'edit_g': not request.g.get('admin', False),
                'edit_s': request.g.get('admin', False),
            }})
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    if request.method == "PUT" or request.method == "POST":
        if not bot.owner == request.g.get('username', '') and not request.g.get('admin', False):
            return Response(status=403)

        body = json.loads(request.body)
        bot.title = body.get('title', bot.title)
        bot.ingress = body.get('ingress', bot.ingress)
        bot.prompt = body.get('prompt', bot.prompt)
        bot.image = body.get('bot_img', bot.image)
        bot.temperature = body.get('temperature', bot.temperature)
        default_model = models.Setting.objects.get(setting_key='default_model').txt_val
        if bot.model == '':
            bot.model = default_model
        if request.g.get('admin', False):
            bot.model = body.get('model', bot.model)
        bot.save()

    if request.method == "DELETE":
        if not bot.owner == request.g.get('username', '') and not request.g.get('admin', False):
            return Response(status=403)
        bot.delete()
        return Response(status=200)

    edit_g = (bot.owner == request.g.get('username', '')
                and request.g['settings']['allow_groups']
                and request.g['dist_to_groups'])

    return Response({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
        'bot_img': bot.image or "bot5.svg",
        'temperature': bot.temperature,
        'model': bot.model,
        'edit_g': edit_g,
        'edit_s': request.g.get('admin', False),
    }})

@api_view(["GET", "PUT"])
def bot_access(request, bot_nr):

    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    if bot_nr != 0:
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    if request.method == "PUT":
        if not request.g.get('admin', False):
            return Response(status=403)
        body = json.loads(request.body)
        school_access = body.get('school_access', False)
        if school_access == False:
            return Response(status=400)
        if not isinstance(school_access, list):
            return Response(status=400)
        if not (school := models.School.objects.get(org_nr=body.get('org_nr', False))):
            return Response(status=404)
        old_accesses = models.BotAccess.objects.filter(bot_nr=bot_nr, school_id=school.org_nr)
        for access in old_accesses:
            access.delete()
        for level in school_access:
            access = models.BotAccess(bot_nr=bot, school_id=school, level=level)
            access.save()
        return Response(status=200)

    access_list = []
    school_list = []
    for school in models.School.objects.all():
        access_list = []
        if bot_nr != 0:
            accesses = models.BotAccess.objects.filter(bot_nr=bot_nr, school_id=school.org_nr)
            for access in accesses:
                access_list.append(access.level)
        school_list.append({
            'org_nr': school.org_nr,
            'school_name': school.school_name,
            'access_list': access_list
        })
    return Response({
        "schoolAccess": school_list,
    })


@api_view(["GET", "PUT"])
def bot_groups(request, bot_nr):

    def get_groups():
        subjects = []
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
                            })
            return subjects

    if not request.g.get('employee', False) and not request.g.get('admin', False):
        return HttpResponseForbidden()

    if bot_nr != 0:
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    if request.method == "PUT":
        body = json.loads(request.body)

        if groups := body.get('groups', False):
            if (
                bot.owner != request.g.get('username') 
                or not request.g['settings']['allow_groups'] 
                or not request.g['dist_to_groups']):
                return Response(status=403)

            acls_to_remove = []
            for subject in groups:
                if acl := models.SubjectAccess.objects.filter(bot_nr=bot_nr, subject_id=subject.get('id', False)).first():
                    if subject.get('checked', False) == False:
                        acls_to_remove.append(acl)
                else:
                    if subject.get('checked', False) == True:
                        acl = models.SubjectAccess(bot_nr=bot, subject_id=subject.get('id', False))
                        acl.save()
            for acl in acls_to_remove:
                acl.delete()

        return Response(status=200)

    access_list = []
    lifespan = models.Setting.objects.get(setting_key='lifespan').int_val
    if bot_nr != 0 and bot.pk:
        for subj in bot.subjects.all():
            if (subj.created and 
                    (subj.created.replace(tzinfo=None) + timedelta(hours=lifespan) < datetime.now())):
                subj.delete()
            else:
                access_list.append(subj.subject_id)
    groups = get_groups()
    groups = [dict(group, checked=group.get('id') in access_list) for group in groups]
    return Response({
        'groups': groups,
        'lifespan': lifespan,
        })

@api_view(["GET", "PUT"])
def settings(request):
    
        if not request.g.get('admin', False):
            return HttpResponseForbidden()
    
        if request.method == "PUT":
            body = json.loads(request.body)
            if setting_body := body.get('setting', False):
                setting = models.Setting.objects.get(setting_key=setting_body.get('setting_key'))
                if setting.is_txt:
                    setting.txt_val = setting_body.get('value', setting.txt_val)
                else:
                    setting.int_val = setting_body.get('value', setting.int_val)
                setting.save()
                return Response(status=200)
            else:    
                return Response(status=400)
    
        settings = models.Setting.objects.all()
        setting_response = [
            {
                'setting_key': setting.setting_key,
                'label': setting.label,
                'value': setting.txt_val if setting.is_txt else setting.int_val,
                'type': 'text' if setting.is_txt else 'number',
            }
            for setting in settings
        ]
        return Response({'settings': setting_response})

@api_view(["GET", "PUT"])
def school_access(request):
    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "PUT":
        body = json.loads(request.body)
        school_body = body.get('school', False)  
        school = models.School.objects.get(org_nr=school_body.get('org_nr') )
        school.access = school_body.get('access', 'none')
        if school.access == 'levels':
            school.school_accesses.all().delete()
            for level in school_body.get('access_list', []):
                access = models.SchoolAccess(school_id=school, level=level)
                access.save()
                print(access)
        school.save()
        return Response(status=200)
    
    schools = models.School.objects.all()
    response = []
    for school in schools:
        if school.access == 'levels':
            access_list = [access.level for access in school.school_accesses.all()]
        else:
            access_list = []
        response.append({
            'org_nr': school.org_nr,
            'school_name': school.school_name,
            'access': school.access,
            'access_list': access_list,
        })
    
    return Response({'schools': response})

@api_view(["POST"])
def start_message(request, bot_nr):
    try:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    return Response({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
    }})


async def send_message(request):
    body = json.loads(request.body)
    bot_nr = body.get('bot_nr')
    messages = body.get('messages')
    if not bot_nr in request.g.get('bots', []):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()

    async def stream():
        completion = await azureClient.chat.completions.create(
            model=bot.model,
            messages=messages,
            temperature=float(bot.temperature),
            stream=True,
            )
        # Mock function for loadtesting etc.:
        # completion = await mock_acreate()
        async for line in completion:
            if line.choices:
                print(line.choices[0].delta.content or "", end="")
                chunk = line.choices[0].delta.content or ""
                if chunk:
                    yield chunk

    return StreamingHttpResponse(stream(), content_type='text/event-stream')
