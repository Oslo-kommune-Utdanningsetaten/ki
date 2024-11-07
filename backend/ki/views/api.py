from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from datetime import datetime, timedelta
import requests
from openai import AsyncAzureOpenAI
from openai import OpenAI, BadRequestError
import os
import json
# from ..mock import mock_acreate


azureClient = AsyncAzureOpenAI(
    azure_endpoint=os.environ.get('OPENAI_API_BASE'),
    api_key=os.environ.get('OPENAI_API_KEY'),
    api_version=os.environ.get('OPENAI_API_VERSION'),
)

huggingfaceClient = OpenAI(
	base_url=os.environ.get('HUGGINGFACE_API_BASE_URL'),
	api_key=os.environ.get('HUGGINGFACE_API_KEY')
)


async def use_log(bot, request, message_length):
    role = 'student'
    role = 'employee' if request.g.get('employee', False) else role
    role = 'admin' if request.g.get('admin', False) else role
    log_line = models.UseLog()
    log_line.role = role
    log_line.bot_id = bot.uuid
    log_line.message_length = message_length
    await log_line.asave()
   
    for school in request.g.get('schools', []):
        await models.LogSchool(
            school_id=school,
            log_id=log_line
        ).asave()


def get_groups(request):
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
            'is_author': request.g.get('author', False),
            'edit_g': edit_g,
        }
    })

@api_view(["PUT"])
def favorite(request, bot_uuid):
    if not request.session.get('user.username', None):
        return Response(status=403)
    if not request.g.get('employee', False):
        return Response(status=403)

    if not str(bot_uuid) in request.g.get('bots', []):
        return Response(status=403)

    try:
        bot = models.Bot.objects.get(uuid=bot_uuid)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    if request.method == "PUT":
        if favorite := bot.favorites.filter(user_id=request.g.get('username', '')).first():
            favorite.delete()
            return Response({'favorite': False})
        else:
            favorite = models.Favorite(
                bot_id=bot, user_id=request.g.get('username', ''))
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

    open_for_distribution = (request.g['settings']['allow_groups'] 
                            and request.g['dist_to_groups'])

    tag_categories = []
    for category in models.TagCategory.objects.all():
        tag_categories.append({
            'id': category.category_id,
            'label': category.category_name,
            'order': category.category_order,
            'tag_items': [
                {
                    'id': tag.tag_label_id,
                    'label': tag.tag_label_name,
                    'order': tag.tag_label_order,
                }
                for tag in category.tag_labels.all()
            ],
        })

    users_bots = [models.Bot.objects.get(uuid=bot_id)
                  for bot_id in request.g.get('bots', [])]
    return_bots = [
        {
            'uuid': bot.uuid,
            'bot_title': bot.title,
            'favorite': True 
                    if (bot.favorites.filter(user_id=request.g.get('username', '')).first())
                    else False,
            'mandatory': bot.mandatory,
            'img_bot': bot.img_bot,
            'avatar_scheme': [int(a) for a in bot.avatar_scheme.split(',')] if bot.avatar_scheme else [0, 0, 0, 0, 0, 0, 0],
            'personal': not bot.library,
            'allow_distribution': bot.allow_distribution and open_for_distribution,
            'bot_info': bot.bot_info or '',
            'tag': bot.tags.all().values_list('tag_value', flat=True) if bot.library else [],
        }
        for bot in users_bots]

    return Response({
        'bots': return_bots,
        'tag_categories': tag_categories,
        'status': 'ok',
        'view_filter': request.g['settings']['view_filter'],
    })


@api_view(["GET"])
def empty_bot(request, lib):

    library = lib == 'library'
    is_admin = request.g.get('admin', False)
    is_employee = request.g.get('employee', False)
    is_author = request.g.get('author', False)
    edit_groups = (request.g['settings']['allow_groups']
                  and request.g['dist_to_groups'])
    default_model = models.Setting.objects.get(
        setting_key='default_model').txt_val

    if not is_admin and not is_employee:
        return Response(status=403)
    if not is_admin and not is_author:
        library = False

    school_access_list = []
    if library:
        school_list = []
        if is_admin:
            school_list = models.School.objects.all()
        elif is_author:
            school_list = [request.g.get('auth_school')]
        for school in school_list:
            school_access_list.append({
                'org_nr': school.org_nr,
                'school_name': school.school_name,
                'access': 'none',
                'access_list': [],
            })

    return Response({
        'bot': {
            'title': '',
            'ingress': '',
            'prompt': '',
            'bot_info': '',
            'prompt_visibility': True,
            'allow_distribution': True,
            'mandatory': False,
            'bot_img': "bot5.svg",
            'avatar_scheme': [0, 0, 0, 0, 0, 0, 0],
            'temperature': '1',
            'model': default_model,
            'edit': True,
            'distribute': edit_groups,
            'choices': [],
            'groups': get_groups(request) if edit_groups and not library else [],
            'schoolAccesses': school_access_list,
            'library': library,
            'tags': [[], [], []],
            'tag_categories': json.loads(request.g['settings']['tag_categories']) if library else [],
        },
        'lifespan': models.Setting.objects.get(setting_key='lifespan').int_val,
    })

@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def bot_info(request, bot_uuid=None):

    is_admin = request.g.get('admin', False)
    is_employee = request.g.get('employee', False)
    is_author = request.g.get('author', False)
    edit_groups = (request.g['settings']['allow_groups']
                  and request.g['dist_to_groups'])

    new_bot = False if bot_uuid else True

    # get bot
    if request.method == "POST":  # Make new bot on POST
        if not new_bot:
            return Response(status=409)
        bot = models.Bot()
        bot.owner = request.g.get('username')
    else: # Get existing bot
        try:
            bot = models.Bot.objects.get(uuid=bot_uuid)
        except models.Bot.DoesNotExist:
            return Response(status=404)

    # build access control
    edit = False
    distribute = False
    is_owner = bot.owner == request.g.get('username', None)
    if is_admin:
        edit = True
        distribute = False
    elif is_employee:
        if is_owner:
            edit = True
            distribute = edit_groups
        elif bot.allow_distribution and bot.library:
            edit = False
            distribute = edit_groups

    # save bot
    if request.method == "PUT" or request.method == "POST":
        if not is_owner and not is_author and not is_admin:
            return Response(status=403)

        def array_to_tag(arr):
            return sum([1 << tag.get('order') for tag in arr if tag.get('checked', False)])
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
        bot.avatar_scheme = ','.join([str(a) for a in body.get('avatar_scheme', bot.avatar_scheme)]) if body.get('avatar_scheme', False) else bot.avatar_scheme
        bot.temperature = body.get('temperature', bot.temperature)
        bot.library = body.get('library', bot.library)
        bot.owner = body.get('owner', bot.owner) if is_admin else bot.owner
        bot.owner = None if bot.owner == '' else bot.owner
        default_model = models.Setting.objects.get(
            setting_key='default_model').txt_val
        if not bool(bot.model):
            bot.model = default_model
        if is_admin or (is_author and is_owner):
            bot.model = body.get('model', bot.model)
        if body.get('tag_categories', False):
            for tag_category in body.get('tag_categories', []):
                tag_obj = bot.tags.filter(category_id=tag_category.get('id')).first()
                if not tag_obj:
                    tag_obj = models.Tag(bot_id=bot, category_id_id=tag_category.get('id'))
                tag_obj.tag_value = array_to_tag([
                        {'order': tag.get('order'), 'checked': tag.get('checked')} 
                        for tag in tag_category.get('tags', [])])
                tag_obj.save()
        bot.save()
        
        # save choices and options
        # delete all choices and options before saving new ones
        if not new_bot:
            for choice in bot.prompt_choices.all():
                choice.options.all().delete()
                choice.delete()

        for choice in body.get('choices', []):
            prompt_choice = models.PromptChoice(
                    id=choice.get('id'),
                    bot_id=bot,
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
        
        # save school access
        if is_admin or is_author:
            for school in body.get('schoolAccesses', []):
                school_obj = models.School.objects.get(org_nr=school.get('org_nr'))
                if is_author and school_obj != request.g.get('auth_school'):
                    continue
                bot_access = school_obj.accesses.filter(bot_id=bot).first()
                if bot_access:
                    bot_access.access = school.get('access', 'none')
                else:
                    bot_access = models.BotAccess(
                        bot_id=bot, school_id=school_obj, access=school.get('access', 'none'))
                if bot_access.access == 'levels':
                    if not new_bot:
                        bot_access.levels.all().delete()
                    for level in school.get('access_list', []):
                        access = models.BotLevel(access_id=bot_access, level=level)
                        access.save()
                bot_access.save() 

    # save groups
    if request.method == "PUT" or request.method == "POST" or request.method == "PATCH":
        if distribute:
            if not is_owner and not distribute:
                return Response(status=403)

            for group in json.loads(request.body).get('groups', []):
                if acl := models.SubjectAccess.objects.filter(bot_id=bot, subject_id=group.get('id')).first():
                    if group.get('checked', False) == False:
                        acl.delete()
                else:
                    if group.get('checked', False) == True:
                        acl = models.SubjectAccess(
                            bot_id=bot, subject_id=group.get('id'))
                        acl.save()

        return Response({'bot': {'uuid': bot.uuid }})

    if request.method == "DELETE":
        if not is_owner and not is_admin:
            return Response(status=403)
        bot.delete()
        return Response(status=200)

    # build response
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

    group_list = []
    if distribute:
        access_list = []
        lifespan = models.Setting.objects.get(setting_key='lifespan').int_val
        for subj in bot.subjects.all():
            if (subj.created and
                    (subj.created.replace(tzinfo=None) + timedelta(hours=lifespan) < datetime.now())):
                subj.delete()
            else:
                access_list.append(subj.subject_id)
        groups = get_groups(request)
        group_list = [dict(group, checked=group.get('id') in access_list)
                for group in groups]

    school_access_list = []
    school_list = []
    if is_admin:
        school_list = models.School.objects.all()
    elif is_author:
        school_list = [request.g.get('auth_school')]
    for school in school_list:
        if new_bot:
            school_access_list.append({
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
            school_access_list.append({
                'org_nr': school.org_nr,
                'school_name': school.school_name,
                'access': bot_access.access if bot_access else 'none',
                'access_list': access_list,
            })

    tag_categories = []
    for category in models.TagCategory.objects.all().order_by('category_order'):
        tag_obj = bot.tags.filter(category_id=category.category_id).first()
        tag_items = []
        for tag_label in category.tag_labels.all().order_by('tag_label_order'):
            tag_items.append({
                'id': tag_label.tag_label_id,
                'label': tag_label.tag_label_name,
                'order': tag_label.tag_label_order,
                'value': tag_obj.tag_value if tag_obj else 'ingen',
                'checked': bool(tag_obj.tag_value >> tag_label.tag_label_order & 1) if tag_obj else False,
            })
        tag_categories.append({
            'id': category.category_id,
            'label': category.category_name,
            'order': category.category_order,
            'tags': tag_items,
        })

    return Response({
        'bot': {
            'uuid': bot.uuid,
            'title': bot.title,
            'ingress': bot.ingress,
            'prompt': bot.prompt,
            'bot_info': bot.bot_info,
            'img_bot': bot.img_bot,
            'prompt_visibility': bot.prompt_visibility,
            'allow_distribution': bot.allow_distribution,
            'mandatory': bot.mandatory,
            'library': bot.library,
            'avatar_scheme': [int(a) for a in bot.avatar_scheme.split(',')] if bot.avatar_scheme else [0, 0, 0, 0, 0, 0, 0],
            'temperature': bot.temperature,
            'model': bot.model,
            'edit': edit,
            'distribute': distribute,
            'owner': bot.owner if is_admin else None,
            'choices': choices,
            'groups': group_list if distribute else None,
            'schoolAccesses': school_access_list if is_admin or is_author else None,
            'tag_categories': tag_categories,
        },
        'lifespan': models.Setting.objects.get(setting_key='lifespan').int_val,
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
def start_message(request, uuid):
    try:
        bot = models.Bot.objects.get(uuid=uuid)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    return Response({'bot': {
        'uuid': bot.uuid,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
    }})


async def send_message(request):
    body = json.loads(request.body)
    bot_uuid = body.get('uuid')
    messages = body.get('messages')
    if not bot_uuid in request.g.get('bots', []):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(uuid=bot_uuid)
        bot_model = bot.model
        if not bool(bot_model):
            bot_model = await models.Setting.objects.aget(setting_key='default_model').txt_val
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()

    await use_log(bot, request, len(messages))

    if (bot_model == 'norallm'):
        return StreamingHttpResponse(streamFromHuggingface(messages, bot.temperature), content_type='text/event-stream')
    else:
        return StreamingHttpResponse(streamFromAzure(messages, bot_model, bot.temperature), content_type='text/event-stream')


async def streamFromHuggingface(messages, temperature):
    completion = huggingfaceClient.chat.completions.create(
        model="nora-normistral-7b-warm-instruct",
        messages=messages,
        stream=True,
        temperature=float(temperature),
        frequency_penalty=float(0.2),
        max_tokens=500,
        top_p=float(0.9),
        stop=["<|im_end|>"]
    )
    for line in completion:
        message = line.choices[0].delta.content or ""
        if len(message):
            yield message


async def streamFromAzure(messages, bot_model, temperature):
    try:
        completion = await azureClient.chat.completions.create(
            model=bot_model,
            messages=messages,
            temperature=float(temperature),
            stream=True,
        )
    except BadRequestError as e:
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


# @api_view(["POST"])
async def send_img_message(request):
    body = json.loads(request.body)
    bot_uuid = body.get('uuid')
    prompt = body.get('prompt')
    if not bot_uuid in request.g.get('bots', []):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(uuid=bot_uuid)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()

    try:
        response = await azureClient.images.generate(
            model=bot.model,
            # model='dall-e-3',
            size='1024x1024',
            quality='standard',
            prompt=prompt,
            response_format='url',
            n=1,
        )
        json_response = json.loads(response.model_dump_json())
        data = json_response['data'][0]
    except BadRequestError as e:
        if e.code == "content_policy_violation":
            data ={'msg': "Dette er ikke et passende emne. Velg noe annet å lage bilde av."}
        else:
            data ={'msg': "Noe gikk galt. Prøv igjen senere."}

    await use_log(bot, request, 1)
    return JsonResponse(data)
