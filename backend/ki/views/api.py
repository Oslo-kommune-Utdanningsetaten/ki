from ki import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime, timedelta, timezone
import json
from ki.ai_providers.azure import chat_completion_azure_streamed, generate_image_azure
from ki.utils import use_log, get_user_data_from_g, get_groups_from_g, aarstrinn_codes, get_setting, get_setting_async


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
def school_list(request):
    if not request.session.get('user.username', None):
        return Response(status=403)
    if not request.g.get('admin', False):
        return Response(status=403)

    schools = []
    for school in models.School.objects.all():
        schools.append({
            'org_nr': school.org_nr,
            'school_name': school.school_name,
        })

    return Response({'schools': schools})

@api_view(["GET"])
def app_config(request):
    info_page_links = []
    info_pages = models.PageText.objects.all()

    if request.session.get('user.username', None):
        for page in info_pages:
            if page.public or request.g.get('employee', False) or request.g.get('admin', False):
                info_page_links.append({
                    'title': page.page_title,
                    'url': f'/info/{page.page_id}',
                })

    # Get default model
    default_model_id = get_setting('default_model')
    default_model_obj = models.BotModel.objects.get(model_id=default_model_id)
    default_model = {
        'model_id': default_model_obj.model_id,
        'display_name': default_model_obj.display_name,
        'model_description': default_model_obj.model_description,
        'deployment_id': default_model_obj.deployment_id,
        'training_cutoff': default_model_obj.training_cutoff,
    }

    return Response({
        'info_pages': info_page_links,
        'role': {
            'is_admin': request.g.get('admin', False),
            'is_employee': request.g.get('employee', False),
            'is_author': request.g.get('author', False),
        },
        'default_model': default_model,
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
def bot_models(request):
    bot_models = models.BotModel.objects.all()
    return Response({
        'models': [
            {
                'deployment_id': model.deployment_id,
                'model_id': model.model_id,
                'display_name': model.display_name,
                'model_description': model.model_description,
                'training_cutoff': model.training_cutoff,
            }
            for model in bot_models
        ]
    })

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
                    'weight': tag.tag_label_weight,
                    'checked': False,
                }
                for tag in category.tag_labels.all()
            ],
        })

    users_bots = [models.Bot.objects.get(uuid=bot_id)
                  for bot_id in request.g.get('bots', [])]

    if request.g.get('admin', False):
        for bot in users_bots:
            bot.access_count = bot.accesses.exclude(access='none').count()

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
            'allow_distribution': bot.allow_distribution,
            'bot_info': bot.bot_info or '',
            'tag': bot.tags.all().values('category_id', 'tag_value') if bot.library else [],
            'access_count': bot.access_count if request.g.get('admin', False) else 0,
        }
        for bot in users_bots]

    return Response({
        'bots': return_bots,
        'tag_categories': tag_categories,
        'status': 'ok',
        'is_bot_filtering_enabled': get_setting('is_bot_filtering_enabled'),
    })


@api_view(["GET"])
def user_info(request):
    # Roles
    roles = []
    role = 'student'
    if request.g.get('employee', False):
        role = 'employee'
        roles.append(role)
    if request.g.get('admin', False):
        role = 'admin'
        roles.append(role)
    # Schools
    schools = []
    for school in request.g.get('schools', []):
        schools.append({
            'org_nr': school.org_nr,
            'school_name': school.school_name,
        })
    # Levels
    level = None
    if (levels := request.g.get('levels', None)) and role == 'student':
        level = min([ aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])

    return Response({
        'user': {
            'username': request.g.get('username', None),
            'name': request.g.get('name', None),
            'is_admin': request.g.get('admin', False),
            'is_employee': request.g.get('employee', False),
            'is_author': request.g.get('author', False),
            'schools': schools,
            'auth_school': request.g.get('auth_school', None),
            'role': role,
            'roles': roles,
            'level': level,
            'levels': request.g.get('levels', None),
        }
    })


@api_view(["GET"])
def empty_bot(request, bot_type):

    library = bot_type == 'library'
    is_admin = request.g.get('admin', False)
    is_employee = request.g.get('employee', False)
    is_author = request.g.get('author', False)

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

    tag_categories = []
    for category in models.TagCategory.objects.all().order_by('category_order'):
        tag_items = []
        for tag_label in category.tag_labels.all().order_by('tag_label_order'):
            tag_items.append({
                'id': tag_label.tag_label_id,
                'label': tag_label.tag_label_name,
                'order': tag_label.tag_label_order,
                'checked': False,
            })
        tag_categories.append({
            'id': category.category_id,
            'label': category.category_name,
            'order': category.category_order,
            'tags': tag_items,
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
            'is_audio_enabled': False,
            'avatar_scheme': [0, 0, 0, 0, 0, 0, 0],
            'temperature': '1',
            'model': None,
            'edit': True,
            # 'distribute': edit_groups,
            'choices': [],
            'groups': get_groups_from_g(request) if is_admin or is_employee else [],
            'schoolAccesses': school_access_list,
            'library': library,
            'tag_categories': tag_categories,
        },
        'default_lifespan': get_setting('default_lifespan'),
        'max_lifespan': get_setting('max_lifespan'),
    })

@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def bot_info(request, bot_uuid=None):

    is_admin = request.g.get('admin', False)
    is_employee = request.g.get('employee', False)
    is_author = request.g.get('author', False)

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
    is_owner = bot.owner == request.g.get('username', None)

    # save bot
    if request.method == "PUT" or request.method == "POST":
        if not (is_owner or is_author or is_admin):
            return Response(status=403)
        if not (is_employee or is_admin):
            return Response(status=403)

        body = json.loads(request.body)
        bot.title = body.get('title', bot.title)
        bot.ingress = body.get('ingress', bot.ingress)
        bot.prompt = body.get('prompt', bot.prompt)
        bot.bot_info = body.get('bot_info', bot.bot_info)
        bot.prompt_visibility = body.get('prompt_visibility', bot.prompt_visibility)
        bot.allow_distribution = body.get('allow_distribution', bot.allow_distribution)
        bot.mandatory = body.get('mandatory', bot.mandatory)
        bot.is_audio_enabled = body.get('is_audio_enabled', bot.is_audio_enabled) if is_admin else bot.is_audio_enabled
        bot.avatar_scheme = ','.join([str(a) for a in body.get('avatar_scheme', bot.avatar_scheme)]) if body.get('avatar_scheme', False) else bot.avatar_scheme
        bot.temperature = body.get('temperature', bot.temperature)
        bot.library = body.get('library', bot.library)
        bot.owner = body.get('owner', bot.owner) if is_admin else bot.owner
        bot.owner = None if bot.owner == '' else bot.owner
        
        model = body.get('model', False)
        if(        
            (is_admin or (is_author and is_owner)) and
            model and
            model != "none" and
            (model_id := model.get('model_id', False))
        ):
            bot.model_id = models.BotModel.objects.get(model_id=model_id)
        else:
            bot.model_id = None
    
        bot.save()

        # save tags
        if body.get('tag_categories', False):
            def array_to_binary(arr):
                return sum([1 << tag.get('weight') for tag in arr if tag.get('checked', False)])
            for tag_category in body.get('tag_categories', []):
                tag_obj = bot.tags.filter(category_id=tag_category.get('id')).first()
                if not tag_obj:
                    tag_obj = models.Tag(bot_id=bot, category_id_id=tag_category.get('id'))
                tag_obj.tag_value = array_to_binary([
                        {'weight': tag.get('weight'), 'checked': tag.get('checked')} 
                        for tag in tag_category.get('tags', [])])
                tag_obj.save()
        
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
                if is_author and not school.get('access', 'none') in ['none', 'emp']:
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

        def is_valid_dates(from_date_iso, to_date_iso):
            max_lifespan = get_setting('max_lifespan')
            try:
                from_date = datetime.fromisoformat(from_date_iso)
                to_date = datetime.fromisoformat(to_date_iso)
                this_date = datetime.now(timezone.utc)
            except ValueError:
                return False
            if from_date > to_date:
                return False
            if to_date > from_date + timedelta(days=max_lifespan):
                return False
            if to_date < this_date:
                return False
            return True

        users_group_ids = [group['id'] for group in request.g.get('groups', [])]
        for incoming_group in json.loads(request.body).get('groups', []):
            incoming_group_id = incoming_group.get('id')
            if not incoming_group_id in users_group_ids:
                continue
            if incoming_group.get('checked', False):
                valid_from, valid_to = incoming_group.get('valid_range', [None, None])
                if not is_valid_dates(valid_from, valid_to):
                    continue
                if not (subject_access := models.SubjectAccess.objects.filter(bot_id=bot, subject_id=incoming_group_id).first()):
                    subject_access = models.SubjectAccess(
                        bot_id=bot, subject_id=incoming_group_id)
                subject_access.valid_from = valid_from
                subject_access.valid_to = valid_to
                subject_access.save()
            else:
                if subject_access := models.SubjectAccess.objects.filter(bot_id=bot, subject_id=incoming_group_id).first():
                    subject_access.delete()

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
            'options': options,
            'order': choice.order,
            'selected': {
                'id': default_option.id,
                'label': default_option.label,
                'text': default_option.text,
                'order': default_option.order,
            } if default_option else None,
        })

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
            access_dict = []
            bot_access = bot.accesses.filter(school_id=school.org_nr).first()
            if bot_access and bot_access.access == 'levels':
                access_dict = [
                    access.level for access in bot_access.levels.all()]
            school_access_list.append({
                'org_nr': school.org_nr,
                'school_name': school.school_name,
                'access': bot_access.access if bot_access else 'none',
                'access_list': access_dict,
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
                'weight': tag_label.tag_label_weight,
                'checked': bool(tag_obj.tag_value >> tag_label.tag_label_weight & 1) if tag_obj else False,
            })
        tag_categories.append({
            'id': category.category_id,
            'label': category.category_name,
            'order': category.category_order,
            'tags': tag_items,
        })

    bot_model = {
        'model_id': bot.model_id.model_id,
        'display_name': bot.model_id.display_name,
        'model_description': bot.model_id.model_description,
        'deployment_id': bot.model_id.deployment_id,
        'training_cutoff': bot.model_id.training_cutoff,
    } if bot.model_id else None

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
            'is_audio_enabled': bot.is_audio_enabled,
            'avatar_scheme': [int(a) for a in bot.avatar_scheme.split(',')] if bot.avatar_scheme else [0, 0, 0, 0, 0, 0, 0],
            'temperature': bot.temperature,
            'model': bot_model,
            'edit': is_admin or (is_employee and is_owner),
            'owner': bot.owner if is_admin else None,
            'choices': choices,
            'groups': get_groups_from_g(request, bot) if is_employee else [],
            'schoolAccesses': school_access_list if is_admin or is_author else None,
            'tag_categories': tag_categories,
        },
        'default_lifespan': get_setting('default_lifespan'),
        'max_lifespan': get_setting('max_lifespan'),
    })


@api_view(["GET", "PUT"])
def settings(request):

    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "PUT":
        body = json.loads(request.body)
        if setting_body := body.get('setting', False):
            setting_key = setting_body.get('setting_key')
            setting = models.Setting.objects.get(setting_key=setting_key)
            if setting.is_txt:
                setting.txt_val = setting_body.get('value', setting.txt_val)
            else:
                setting.int_val = setting_body.get('value', setting.int_val)
            setting.save()
            return Response(status=200)
        else:
            return Response(status=400)

    all_settings = models.Setting.objects.all()
    setting_response = [
        {
            'setting_key': setting.setting_key,
            'label': setting.label,
            'value': setting.txt_val if setting.is_txt else setting.int_val,
            'type': 'text' if setting.is_txt else 'number',
        }
        for setting in all_settings
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
        school.school_accesses.all().delete()
        if school.access == 'levels':
            for level in school_body.get('access_list', []):
                access = models.SchoolAccess(school_id=school, level=level)
                access.save()
        school.save()
        return Response(status=200)

    schools = models.School.objects.all()
    response = []
    for school in schools:
        access_list = []
        if school.access == 'levels':
            for access in school.school_accesses.all():
                access_list.append(access.level)

        response.append({
            'org_nr': school.org_nr,
            'school_name': school.school_name,
            'access': school.access,
            'access_list': access_list,
        })

    return Response({'schools': response})

@api_view(["GET", "PUT", "DELETE"])
def authors(request):
    if not request.g.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "DELETE":
        body = json.loads(request.body)
        author_body = body.get('author', False)
        full_id = author_body.get('user_id') + '@feide.osloskolen.no'
        author = models.Role.objects.filter(user_id=full_id).first()
        if author:
            author.delete()

    if request.method == "PUT":
        body = json.loads(request.body)
        author_body = body.get('author', False)
        full_id = author_body.get('user_id') + '@feide.osloskolen.no'
        author = models.Role.objects.filter(user_id=full_id).first()
        if not author:
            author = models.Role()
            author.user_id = full_id
            author.role = 'author'
        author.user_name = author_body.get('name')
        author.school = models.School.objects.get(org_nr=author_body.get('school_id'))
        author.save()

    authors = models.Role.objects.filter(role='author').all()
    response = []
    for author in authors:
        response.append({
            'user_id': author.user_id.split('@')[0],
            'name': author.user_name or '',
            'school_id': author.school.org_nr,
        })

    return Response({'authors': response})

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
        try:
            bot_model_obj = await models.BotModel.objects.aget(model_id=bot.model_id_id)
        except models.BotModel.DoesNotExist:
            default_model_id = await get_setting_async('default_model')
            bot_model_obj = await models.BotModel.objects.aget(model_id=default_model_id)
        bot_model = bot_model_obj.deployment_id
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()
    level, schools, role = get_user_data_from_g(request)
    await use_log(bot_uuid, role=role, level=level, schools=schools, message_length=len(messages), interaction_type='text')
    return await chat_completion_azure_streamed(messages, bot_model, temperature=bot.temperature)


async def send_img_message(request):
    body = json.loads(request.body)
    bot_uuid = body.get('uuid')
    messages = body.get('messages')
    prompt = messages[-1].get('content')
    if not bot_uuid in request.g.get('bots', []):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(uuid=bot_uuid)
        bot_model_obj = await models.BotModel.objects.aget(model_id=bot.model_id_id)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()
    level, schools, role = get_user_data_from_g(request)
    await use_log(bot_uuid, role=role, level=level, schools=schools, message_length=len(messages), interaction_type='text')
    return await generate_image_azure(prompt, model=bot_model_obj.deployment_id)

