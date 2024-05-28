from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime, timedelta
import requests
from openai import AsyncAzureOpenAI
import openai
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
        "content_text": text_line.page_text,
    })


@api_view(["GET"])
def menu_items(request):
    menu_items = []
    info_pages = models.PageText.objects.all()

    if request.session.get('user.username', None):
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
                    'class': 'oslo-text-danger fw-bolder' if page.page_id == 'news' else '',
                })
        menu_items.append({
            'title': 'Startside',
            'url': '/',
            'class': '',
        })

    # user is allowed to edit groups
    edit_g = bool(request.g['settings']['allow_groups']
                  and request.g['dist_to_groups'])

    return Response({
        'menuItems': menu_items,
        'role': {
            'is_admin': request.g.get('admin', False),
            'is_employee': request.g.get('employee', False),
            'edit_g': edit_g,
        }
    })

@api_view(["PUT"])
def favorite(request, bot_nr):
    if not request.session.get('user.username', None):
        return Response(status=403)
    if not request.g.get('employee', False):
        return Response(status=403)

    if not bot_nr in request.g.get('bots', []):
        return Response(status=403)

    try:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    if request.method == "PUT":
        if favorite := bot.favorites.filter(user_id=request.g.get('username', '')).first():
            favorite.delete()
            return Response({'favorite': False})
        else:
            favorite = models.Favorite(
                bot_nr=bot, user_id=request.g.get('username', ''))
            favorite.save()
            return Response({'favorite': True})

@api_view(["GET"])
def user_bots(request):
    if not request.session.get('user.username', None):
        return Response({
            'status': 'not_feide',
            'bots': None,
        })

    if not request.g.get('has_access', False):
        return Response({
            'status': 'not_school',
            'bots': None,
        })

    users_bots = [models.Bot.objects.get(bot_nr=bot_nr)
                  for bot_nr in request.g.get('bots', [])]
    return_bots = [
        {
            'bot_nr': bot.bot_nr,
            'bot_title': bot.title,
            'bot_img': bot.image or "bot5.svg",
            'favorite': True 
                if (bot.favorites.filter(user_id=request.g.get('username', '')).first() 
                    or bot.bot_nr == 1)
                else False,
            'mandatory': bot.mandatory,
            'personal': bot.owner == request.g.get('username', ''),
            'allow_distribution': bot.allow_distribution,
            'bot_info': bot.bot_info,
            'tag': [bot.tag_cat_1, bot.tag_cat_2, bot.tag_cat_3],
        }
        for bot in users_bots]
    if (request.g.get('admin', False) or
            request.g.get('employee', False) and
            models.Setting.objects.get(setting_key='allow_personal').int_val):
        return_bots.append({
            'bot_nr': 0,
            'bot_title': "Ny bot",
            'bot_img': "pluss.svg",
            'favorite': True,
            'mandatory': True,
            'personal': False,
            'allow_distribution': False,
            'tag': [[0], [0], [0]],
        })

    return Response({
        'bots': return_bots,
        'status': 'ok',
    })


@api_view(["GET", "POST", "PUT", "DELETE"])
def bot_info(request, bot_nr=None):

    is_admin = request.g.get('admin', False)
    new_bot = False

    if (bot_nr and 
        not bot_nr in request.g.get('bots', [])
        and not is_admin):
        return Response(status=403)

    # Make new bot on POST
    if request.method == "POST":
        bot = models.Bot()
        if not request.g.get('admin', False):
            bot.owner = request.g.get('username')
        new_bot = True
    else:
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)
    is_owner = bot.owner == request.g.get('username', None)

    if request.method == "PUT" or request.method == "POST":
        if not is_owner and not is_admin:
            return Response(status=403)

        def array_to_tag(arr):
            return sum([1 << n for n in arr])
        body = json.loads(request.body)
        bot.title = body.get('title', bot.title)
        bot.ingress = body.get('ingress', bot.ingress)
        bot.prompt = body.get('prompt', bot.prompt)
        bot.bot_info = body.get('bot_info', bot.bot_info)
        bot.prompt_visibility = body.get(
            'prompt_visibility', bot.prompt_visibility)
        bot.allow_distribution = body.get(
            'allow_distribution', bot.allow_distribution)
        bot.mandatory = body.get(
            'mandatory', bot.mandatory)
        bot.image = body.get('bot_img', bot.image)
        bot.temperature = body.get('temperature', bot.temperature)
        bot.owner = body.get('owner', bot.owner) if is_admin else bot.owner
        bot.owner = None if bot.owner == '' else bot.owner
        default_model = models.Setting.objects.get(
            setting_key='default_model').txt_val
        if bot.model == '':
            bot.model = default_model
        if is_admin:
            bot.model = body.get('model', bot.model)
        bot.tag_cat_1 = array_to_tag(body.get('tags', [0, 0, 0])[0])
        bot.tag_cat_2 = array_to_tag(body.get('tags', [0, 0, 0])[1])
        bot.tag_cat_3 = array_to_tag(body.get('tags', [0, 0, 0])[2])
        bot.save()
        
        # delete all choices and options
        if not new_bot:
            for choice in bot.prompt_choices.all():
                choice.options.all().delete()
                choice.delete()

        for choice in body.get('choices', []):
            prompt_choice = models.PromptChoice(
                    id=choice.get('id'),
                    bot_nr=bot,
                    label=choice.get('label'),
                    order=choice.get('order'),
                    # text=choice.get('text')
            )
            prompt_choice.save()

            for option in choice.get('options', []):
                choice_option = models.ChoiceOption(
                        id=option.get('id'),
                        choice_id=prompt_choice, 
                        label=option.get('label'), 
                        text=option.get('text'),
                        order=option.get('order'),
                        is_default=choice.get('selected').get('id', 0) == option.get('id')\
                            if choice.get('selected', False) else False
                )
                choice_option.save()

    if request.method == "DELETE":
        if not is_owner and not is_admin:
            return Response(status=403)
        bot.delete()
        return Response(status=200)

    edit = False
    distribute = False
    if is_admin:
        edit = True
        distribute = False
    elif request.g.get('employee', False):
        if is_owner:
            edit = True
            distribute = True
        elif bot.allow_distribution and not bot.owner:
            edit = False
            distribute = True

    choices = []
    for choice in bot.prompt_choices.all():
        options = []
        default_option = choice.options.filter(is_default=True).first()
        for option in choice.options.all():
            options.append({
                'id': option.id,
                'label': option.label,
                'text': option.text,
                'order': option.order,
            })
        choices.append({
            'id': choice.id,
            'label': choice.label,
            # 'text': choice.text,
            'options': options,
            'order': choice.order,
            'selected': {
                'id': default_option.id,
                'label': default_option.label,
                'text': default_option.text,
                'order': default_option.order,
            } if default_option else None,
        })

    def tag_to_array(tag):
        return [n for n in range(30) if (tag >> n & 1)]

    return Response({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
        'bot_info': bot.bot_info,
        'prompt_visibility': bot.prompt_visibility,
        'allow_distribution': bot.allow_distribution,
        'mandatory': bot.mandatory,
        'bot_img': bot.image or "bot5.svg",
        'temperature': bot.temperature,
        'model': bot.model,
        'edit': edit,
        'distribute': distribute,
        'choices': choices,
        'owner': bot.owner if is_admin else None,
        'tags': [tag_to_array(bot.tag_cat_1), tag_to_array(bot.tag_cat_2), tag_to_array(bot.tag_cat_3)],
    }})


@api_view(["GET", "PUT"])
def bot_access(request, bot_nr=None):

    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    new_bot = True if bot_nr is None else False

    if not new_bot:
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    if request.method == "PUT":
        if not request.g.get('admin', False):
            return Response(status=403)
        body = json.loads(request.body)
        if not (school := models.School.objects.get(org_nr=body.get('org_nr', False))):
            return Response(status=404)
        bot_access = school.accesses.filter(bot_nr=bot).first()
        if bot_access:
            bot_access.access = body.get('school_access', 'none')
        else:
            bot_access = models.BotAccess(
                bot_nr=bot, school_id=school, access=body.get('school_access', 'none'))
        if bot_access.access == 'levels':
            bot_access.levels.all().delete()
            for level in body.get('school_access_list', []):
                access = models.BotLevel(access_id=bot_access, level=level)
                access.save()
        bot_access.save()
        return Response(status=200)

    school_list = []
    for school in models.School.objects.all():
        if new_bot:
            school_list.append({
                'org_nr': school.org_nr,
                'school_name': school.school_name,
                'access': 'none',
                'access_list': [],
            })
        else:
            access_list = []
            bot_access = bot.accesses.filter(school_id=school.org_nr).first()
            if bot_access and bot_access.access == 'levels':
                access_list = [
                    access.level for access in bot_access.levels.all()]
            school_list.append({
                'org_nr': school.org_nr,
                'school_name': school.school_name,
                'access': bot_access.access if bot_access else 'none',
                'access_list': access_list,
            })
    return Response({
        "schoolAccess": school_list,
    })


@api_view(["GET", "PUT"])
def bot_groups(request, bot_nr=None):

    def get_groups():
        subjects = []
        access_token = request.session.get('user.auth')['access_token']
        groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        try:
            groupinfo_response = requests.get(
                groupinfo_endpoint, headers=headers)
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

    new_bot = True if bot_nr is None else False

    if not new_bot:
        try:
            bot = models.Bot.objects.get(bot_nr=bot_nr)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    # user is allowed to edit groups
    edit_g = ((new_bot
               or bot.owner == request.g.get('username', '')
               or bot.allow_distribution)
              and request.g['settings']['allow_groups']
              and request.g['dist_to_groups'])

    if not edit_g:
        return Response({
            'edit_g': False,
            'groups': [],
        })

    if request.method == "PUT":
        body = json.loads(request.body)
        if groups := body.get('groups', False):
            acls_to_remove = []
            for subject in groups:
                if acl := models.SubjectAccess.objects.filter(bot_nr=bot_nr, subject_id=subject.get('id', False)).first():
                    if subject.get('checked', False) == False:
                        acls_to_remove.append(acl)
                else:
                    if subject.get('checked', False) == True:
                        acl = models.SubjectAccess(
                            bot_nr=bot, subject_id=subject.get('id', False))
                        acl.save()
            for acl in acls_to_remove:
                acl.delete()

        return Response(status=200)

    access_list = []
    lifespan = models.Setting.objects.get(setting_key='lifespan').int_val
    if not new_bot and bot.pk:
        for subj in bot.subjects.all():
            if (subj.created and
                    (subj.created.replace(tzinfo=None) + timedelta(hours=lifespan) < datetime.now())):
                subj.delete()
            else:
                access_list.append(subj.subject_id)
    groups = get_groups()
    groups = [dict(group, checked=group.get('id') in access_list)
              for group in groups]
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
            setting = models.Setting.objects.get(
                setting_key=setting_body.get('setting_key'))
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
        school = models.School.objects.get(org_nr=school_body.get('org_nr'))
        school.access = school_body.get('access', 'none')
        if school.access == 'levels':
            school.school_accesses.all().delete()
            for level in school_body.get('access_list', []):
                access = models.SchoolAccess(school_id=school, level=level)
                access.save()
        school.save()
        return Response(status=200)

    schools = models.School.objects.all()
    response = []
    for school in schools:
        if school.access == 'levels':
            access_list = [
                access.level for access in school.school_accesses.all()]
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
        try:
            completion = await azureClient.chat.completions.create(
                model=bot.model,
                messages=messages,
                temperature=float(bot.temperature),
                stream=True,
            )
        except openai.BadRequestError as e:
            if e.code == "content_filter":
                yield "Dette er ikke et passende emne. Start samtalen på nytt."
            else:
                yield "Noe gikk galt. Prøv igjen senere."
            return
        async for line in completion:
            if line.choices:
                chunk = line.choices[0].delta.content or ""
                if line.choices[0].finish_reason == "content_filter":
                    yield "\n\nBeklager, vi stopper her! Dette er ikke passende innhold å vise. Start samtalen på nytt."
                    break
                if line.choices[0].finish_reason == "length":
                    print(line.choices[0].content_filter_results)
                    yield "\n\nGrensen for antall tegn i samtalen er nådd."
                    break
                if chunk:
                    yield chunk

    return StreamingHttpResponse(stream(), content_type='text/event-stream')
