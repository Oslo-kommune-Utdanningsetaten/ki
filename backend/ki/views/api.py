from ki import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseNotFound, HttpResponseForbidden
from datetime import datetime, timedelta, timezone
import json
from ki.ai_providers.azure import chat_completion_azure_streamed, generate_image_azure
from ki.utils import use_log, get_user_data_from_userinfo, generate_group_access_list, aarstrinn_codes, get_setting, get_setting_async


@api_view(["GET"])
def page_text(request, page):
    try:
        text_line = models.PageText.objects.get(page_id=page)
    except models.PageText.DoesNotExist:
        return Response(status=404)

    if (not request.userinfo.get('employee', False)
        and not request.userinfo.get('admin', False)
            and not text_line.public):
        return Response(status=403)

    return Response({
        "page": page,
        "contentText": text_line.page_text,
    })

@api_view(["GET"])
def school_list(request):
    if not request.session.get('user.username', None):
        return Response(status=403)
    if not request.userinfo.get('admin', False):
        return Response(status=403)

    schools = []
    for school in models.School.objects.all():
        schools.append({
            'orgNr': school.org_nr,
            'schoolName': school.school_name,
        })

    return Response({'schools': schools})

@api_view(["GET"])
def app_config(request):
    info_page_links = []
    info_pages = models.PageText.objects.all()

    if request.session.get('user.username', None):
        for page in info_pages:
            if page.public or request.userinfo.get('employee', False) or request.userinfo.get('admin', False):
                info_page_links.append({
                    'title': page.page_title,
                    'url': f'/info/{page.page_id}',
                })

    # Get default model
    default_model_id = get_setting('default_model')
    default_model_obj = models.BotModel.objects.get(model_id=default_model_id)
    default_model = {
        'modelId': default_model_obj.model_id,
        'displayName': default_model_obj.display_name,
        'modelDescription': default_model_obj.model_description,
        'deploymentId': default_model_obj.deployment_id,
        'trainingCutoff': default_model_obj.training_cutoff,
    }
    is_external_user = request.userinfo.get('external_user', False)
    has_self_service = request.session.get('user.has_self_service', False)

    return Response({
        'infoPages': info_page_links,
        'role': {
            'isAdmin': request.userinfo.get('admin', False),
            'isEmployee': request.userinfo.get('employee', False),
            'isAuthor': request.userinfo.get('author', False),
            'hasSelfService': is_external_user and has_self_service,
        },
        'defaultModel': default_model,
    })


@api_view(["PUT"])
def favorite(request, bot_uuid):
    if not request.session.get('user.username', None):
        return Response(status=403)
    if not request.userinfo.get('employee', False):
        return Response(status=403)

    if not str(bot_uuid) in request.userinfo.get('bots', []):
        return Response(status=403)

    try:
        bot = models.Bot.objects.get(uuid=bot_uuid)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    if request.method == "PUT":
        if favorite := bot.favorites.filter(user_id=request.userinfo.get('username', '')).first():
            favorite.delete()
            return Response({'favorite': False})
        else:
            favorite = models.Favorite(
                bot_id=bot, user_id=request.userinfo.get('username', ''))
            favorite.save()
            return Response({'favorite': True})

@api_view(["GET"])
def bot_models(request):
    bot_models = models.BotModel.objects.all()
    return Response({
        'models': [
            {
                'deploymentId': model.deployment_id,
                'modelId': model.model_id,
                'displayName': model.display_name,
                'modelDescription': model.model_description,
                'trainingCutoff': model.training_cutoff,
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

    if not request.userinfo.get('has_access', False):
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
            'tagItems': [
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
                  for bot_id in request.userinfo.get('bots', [])]

    if request.userinfo.get('admin', False):
        for bot in users_bots:
            bot.access_count = bot.accesses.exclude(access='none').count()

    return_bots = [
        {
            'uuid': bot.uuid,
            'botTitle': bot.title,
            'favorite': True 
                    if (bot.favorites.filter(user_id=request.userinfo.get('username', '')).first())
                    else False,
            'mandatory': bot.mandatory,
            'imgBot': bot.img_bot,
            'avatarScheme': [int(a) for a in bot.avatar_scheme.split(',')] if bot.avatar_scheme else [0, 0, 0, 0, 0, 0, 0],
            'personal': not bot.library,
            'allowDistribution': bot.allow_distribution,
            'botInfo': bot.bot_info or '',
            'tag': [{
                'categoryId': tag['category_id'], 
                'tagValue': tag['tag_value']
                } 
                for tag in bot.tags.all().values('category_id', 'tag_value')] if bot.library else [],
            'accessCount': bot.access_count if request.userinfo.get('admin', False) else 0,
        }
        for bot in users_bots]

    return Response({
        'bots': return_bots,
        'tagCategories': tag_categories,
        'status': 'ok',
        'isBotFilteringEnabled': get_setting('is_bot_filtering_enabled'),
    })


@api_view(["GET"])
def user_info(request):
    # Roles
    roles = []
    role = 'student'
    if request.userinfo.get('employee', False):
        role = 'employee'
        roles.append(role)
    if request.userinfo.get('admin', False):
        role = 'admin'
        roles.append(role)
    # Schools
    schools = []
    for school in request.userinfo.get('schools', []):
        schools.append({
            'orgNr': school.org_nr,
            'schoolName': school.school_name,
        })
    
    auth_school = {
        'orgNr': None,
        'schoolName': None,
    }
    if auth_school_obj := request.userinfo.get('auth_school', None):
        auth_school = {
            'orgNr': auth_school_obj.org_nr,
            'schoolName': auth_school_obj.school_name,
        }

    # Levels
    level = None
    if (levels := request.userinfo.get('levels', None)) and role == 'student':
        level = min([ aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])

    return Response({
        'user': {
            'username': request.userinfo.get('username', None),
            'name': request.userinfo.get('name', None),
            'isAdmin': request.userinfo.get('admin', False),
            'isEmployee': request.userinfo.get('employee', False),
            'isAuthor': request.userinfo.get('author', False),
            'schools': schools,
            'authSchool': auth_school,
            'role': role,
            'roles': roles,
            'level': level,
            'levels': request.userinfo.get('levels', None),
        }
    })


@api_view(["GET"])
def external_users(request):
    is_admin = request.userinfo.get('admin', False)
    if not is_admin:
        return Response(status=403)

    users = models.ExternalUser.objects.all().order_by('name')
    return Response({
        'users': [{
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'hasSelfService': user.has_self_service,
            'expired': user.valid_to < datetime.now(timezone.utc) if user.valid_to else True,
        } for user in users]
    })


@api_view(["GET", "POST", "PUT", "DELETE"])
def external_user_info(request, user_id=None):

    is_admin = request.userinfo.get('admin', False)

    if is_admin:

        # Create new user
        if request.method == "POST":
            body = json.loads(request.body)
            user_body = body.get('user', False)
            user = models.ExternalUser()
            user.set_username(user_body.get('username', user.username))
            user.name = user_body.get('name', user.name)
            user.has_self_service = user_body.get('hasSelfService', False)
            user.valid_to = user_body.get('validTo', None)
            user.memberships = user_body.get('memberships', [])
            if 'newPassword' in user_body:
                user.set_password(user_body['password'])
            user.save()
            return Response(status=200)

        # Get existing user from user_id parameter
        if not user_id:
            return Response(status=400)
        user = models.ExternalUser.objects.get(id=user_id)
        if not user:
            return Response(status=400)

        if request.method == "DELETE":
            try:
                user.delete()
                return Response(status=200)
            except models.ExternalUser.DoesNotExist:
                return Response(status=404)

        if request.method == "PUT":
            body = json.loads(request.body)
            user_body = body.get('user', None)
            if not user_body:
                return Response(status=400)
            user.name = user_body.get('name', user.name)
            if 'newPassword' in user_body:
                try:
                    user.set_password(user_body.get('newPassword', user.password))
                except ValueError as e:
                    return Response(status=404, data={"error": str(e)})
            try:
                user.set_username(user_body.get('username', user.username), user.username)
            except ValueError as e:
                return Response(status=404, data={"error": str(e)})
            user.has_self_service = user_body.get('hasSelfService', user.has_self_service)
            valid_to_str = user_body.get('validTo', None)
            if valid_to_str:
                dt = datetime.fromisoformat(valid_to_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                user.valid_to = dt
            user.memberships = user_body.get('memberships', user.memberships)
            user.save()
            return Response(status=200)

        if request.method == "GET":
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'hasSelfService': user.has_self_service,
                    'validTo': user.valid_to.isoformat() if user.valid_to else None,
                    'memberships': user.memberships,
                }
            })

    else:
        # Uptate user info from self-service
        if request.session["user.auth_method"] != "local":
            return Response(status=403)
        user_id = request.session["user.id"]
        user = models.ExternalUser.objects.get(id=user_id)
        if not user:
            return Response(status=404)
        if not user.has_self_service:
            return Response(status=403)
    
        if request.method == "PUT":
            body = json.loads(request.body)
            user_body = body.get('user', None)
            if not user_body:
                return Response(status=400)
            user.name = user_body.get('name', user.name)
            # user.username = user_body.get('username', user.username)
            if 'newPassword' in user_body and 'password' in user_body:
                if not user.check_password(user_body['password']):
                    return Response(status=403, data={"error": "Gammelt passord er feil"})
                try:
                    user.set_password(user_body.get('newPassword', user.password))
                except ValueError as e:
                    return Response(status=404, data={"error": str(e)})
            user.save()
            return Response(status=200)
        
        if request.method in ["POST", "DELETE"]:
            return Response(status=405)

        if request.method == "GET":
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                }
            })


@api_view(["GET"])
def empty_bot(request, bot_type):

    library = bot_type == 'library'
    is_admin = request.userinfo.get('admin', False)
    is_employee = request.userinfo.get('employee', False)
    is_author = request.userinfo.get('author', False)

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
            school_list = [request.userinfo.get('auth_school')]
        for school in school_list:
            school_access_list.append({
                'orgNr': school.org_nr,
                'schoolName': school.school_name,
                'access': 'none',
                'accessList': [],
            })

    tag_categories = []
    for category in models.TagCategory.objects.all().order_by('category_order'):
        tag_items = []
        for tag_label in category.tag_labels.all().order_by('tag_label_order'):
            tag_items.append({
                'id': tag_label.tag_label_id,
                'label': tag_label.tag_label_name,
                'order': tag_label.tag_label_order,
                'weight': tag_label.tag_label_weight,
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
            'botInfo': '',
            'promptVisibility': True,
            'allowDistribution': True,
            'mandatory': False,
            'isAudioEnabled': False,
            'avatarScheme': [0, 0, 0, 0, 0, 0, 0],
            'temperature': '1',
            'model': None,
            'edit': True,
            # 'distribute': edit_groups,
            'choices': [],
            'schoolAccesses': school_access_list,
            'library': library,
            'tagCategories': tag_categories,
        },
        'defaultLifespan': get_setting('default_lifespan'),
        'maxLifespan': get_setting('max_lifespan'),
    })

@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def bot_info(request, bot_uuid=None):

    is_admin = request.userinfo.get('admin', False)
    is_employee = request.userinfo.get('employee', False)
    is_author = request.userinfo.get('author', False)

    new_bot = False if bot_uuid else True

    # get bot
    if request.method == "POST":  # Make new bot on POST
        if not new_bot:
            return Response(status=409)
        bot = models.Bot()
        bot.owner = request.userinfo.get('username')
    else: # Get existing bot
        try:
            bot = models.Bot.objects.get(uuid=bot_uuid)
        except models.Bot.DoesNotExist:
            return Response(status=404)
    is_owner = bot.owner == request.userinfo.get('username', None)

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
        bot.bot_info = body.get('botInfo', bot.bot_info)
        bot.prompt_visibility = body.get('promptVisibility', bot.prompt_visibility)
        bot.allow_distribution = body.get('allowDistribution', bot.allow_distribution)
        bot.mandatory = body.get('mandatory', bot.mandatory)
        bot.is_audio_enabled = body.get('isAudioEnabled', bot.is_audio_enabled) if is_admin else bot.is_audio_enabled
        bot.avatar_scheme = ','.join([str(a) for a in body.get('avatarScheme', bot.avatar_scheme)]) if body.get('avatarScheme', False) else bot.avatar_scheme
        bot.temperature = body.get('temperature', bot.temperature)
        bot.library = body.get('library', bot.library)
        bot.owner = body.get('owner', bot.owner) if is_admin else bot.owner
        bot.owner = None if bot.owner == '' else bot.owner
        
        model = body.get('model', False)
        if(        
            (is_admin or (is_author and is_owner)) and
            model and
            model != "none" and
            (model_id := model.get('modelId', False))
        ):
            bot.model_id = models.BotModel.objects.get(model_id=model_id)
        else:
            bot.model_id = None
    
        bot.save()

        # save tags
        if body.get('tagCategories', False):
            def array_to_binary(arr):
                return sum([1 << tag.get('weight') for tag in arr if tag.get('checked', False)])
            for tag_category in body.get('tagCategories', []):
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
                school_obj = models.School.objects.get(org_nr=school.get('orgNr'))
                if is_author and school_obj != request.userinfo.get('authSchool'):
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
                    for level in school.get('accessList', []):
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

        users_group_ids = [group['id'] for group in request.userinfo.get('groups', [])]
        for incoming_group in json.loads(request.body).get('groups', []):
            incoming_group_id = incoming_group.get('id')
            if not incoming_group_id in users_group_ids:
                continue
            if incoming_group.get('checked', False):
                valid_from, valid_to = incoming_group.get('validRange', [None, None])
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
        school_list = [request.userinfo.get('auth_school')]
    for school in school_list:
        if new_bot:
            school_access_list.append({
                'orgNr': school.org_nr,
                'schoolName': school.school_name,
                'access': 'none',
                'accessList': [],
            })
        else:
            access_dict = []
            bot_access = bot.accesses.filter(school_id=school.org_nr).first()
            if bot_access and bot_access.access == 'levels':
                access_dict = [
                    access.level for access in bot_access.levels.all()]
            school_access_list.append({
                'orgNr': school.org_nr,
                'schoolName': school.school_name,
                'access': bot_access.access if bot_access else 'none',
                'accessList': access_dict,
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
        'modelId': bot.model_id.model_id,
        'displayName': bot.model_id.display_name,
        'modelDescription': bot.model_id.model_description,
        'deploymentId': bot.model_id.deployment_id,
        'trainingCutoff': bot.model_id.training_cutoff,
    } if bot.model_id else None

    groups_access_list = []
    if is_employee:
        groups_access_list = generate_group_access_list(request.userinfo.get('groups', []), bot)

    return Response({
        'bot': {
            'uuid': bot.uuid,
            'title': bot.title,
            'ingress': bot.ingress,
            'prompt': bot.prompt,
            'botInfo': bot.bot_info,
            'imgBot': bot.img_bot,
            'promptVisibility': bot.prompt_visibility,
            'allowDistribution': bot.allow_distribution,
            'mandatory': bot.mandatory,
            'library': bot.library,
            'isAudioEnabled': bot.is_audio_enabled,
            'avatarScheme': [int(a) for a in bot.avatar_scheme.split(',')] if bot.avatar_scheme else [0, 0, 0, 0, 0, 0, 0],
            'temperature': bot.temperature,
            'model': bot_model,
            'edit': is_admin or (is_employee and is_owner),
            'owner': bot.owner if is_admin else None,
            'choices': choices,
            'groups': groups_access_list,
            'schoolAccesses': school_access_list if is_admin or is_author else None,
            'tagCategories': tag_categories,
        },
        'defaultLifespan': get_setting('default_lifespan'),
        'maxLifespan': get_setting('max_lifespan'),
    })


@api_view(["GET", "PUT"])
def settings(request):

    if not request.userinfo.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "PUT":
        body = json.loads(request.body)
        if setting_body := body.get('setting', False):
            setting_key = setting_body.get('settingKey')
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
            'settingKey': setting.setting_key,
            'label': setting.label,
            'value': setting.txt_val if setting.is_txt else setting.int_val,
            'type': 'text' if setting.is_txt else 'number',
        }
        for setting in all_settings
    ]
    return Response({'settings': setting_response})


@api_view(["GET", "PUT"])
def school_access(request):
    if not request.userinfo.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "PUT":
        body = json.loads(request.body)
        school_body = body.get('school', False)
        school = models.School.objects.get(org_nr=school_body.get('orgNr'))
        school.access = school_body.get('access', 'none')
        school.school_accesses.all().delete()
        if school.access == 'levels':
            for level in school_body.get('accessList', []):
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
            'orgNr': school.org_nr,
            'schoolName': school.school_name,
            'access': school.access,
            'accessList': access_list,
        })

    return Response({'schools': response})

@api_view(["GET", "PUT", "DELETE"])
def authors(request):
    if not request.userinfo.get('admin', False):
        return HttpResponseForbidden()

    if request.method == "DELETE":
        body = json.loads(request.body)
        author_body = body.get('author', False)
        full_id = author_body.get('userId') + '@feide.osloskolen.no'
        author = models.Role.objects.filter(user_id=full_id).first()
        if author:
            author.delete()

    if request.method == "PUT":
        body = json.loads(request.body)
        author_body = body.get('author', False)
        full_id = author_body.get('userId') + '@feide.osloskolen.no'
        author = models.Role.objects.filter(user_id=full_id).first()
        if not author:
            author = models.Role()
            author.user_id = full_id
            author.role = 'author'
        author.user_name = author_body.get('name')
        author.school = models.School.objects.get(org_nr=author_body.get('schoolId'))
        author.save()

    authors = models.Role.objects.filter(role='author').all()
    response = []
    for author in authors:
        response.append({
            'userId': author.user_id.split('@')[0],
            'name': author.user_name or '',
            'schoolId': author.school.org_nr,
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
    is_admin = request.userinfo.get('admin', False)
    has_bot_access = bot_uuid in request.userinfo.get('bots', [])
    if not (has_bot_access or is_admin):
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
    level, schools, role = get_user_data_from_userinfo(request)
    await use_log(bot_uuid, role=role, level=level, schools=schools, message_length=len(messages), interaction_type='text')
    return await chat_completion_azure_streamed(messages, bot_model, temperature=bot.temperature)


async def send_img_message(request):
    body = json.loads(request.body)
    bot_uuid = body.get('uuid')
    messages = body.get('messages')
    prompt = messages[-1].get('content')
    is_admin = request.userinfo.get('admin', False)
    has_bot_access = bot_uuid in request.userinfo.get('bots', [])
    if not (has_bot_access or is_admin):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(uuid=bot_uuid)
        bot_model_obj = await models.BotModel.objects.aget(model_id=bot.model_id_id)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()
    level, schools, role = get_user_data_from_userinfo(request)
    await use_log(bot_uuid, role=role, level=level, schools=schools, message_length=len(messages), interaction_type='text')
    return await generate_image_azure(prompt, model=bot_model_obj.deployment_id)

