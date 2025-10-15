import requests
import os
import re
from datetime import datetime, timedelta, timezone

aarstrinn_codes = {
    'aarstrinn1': 1,
    'aarstrinn2': 2,
    'aarstrinn3': 3,
    'aarstrinn4': 4,
    'aarstrinn5': 5,
    'aarstrinn6': 6,
    'aarstrinn7': 7,
    'aarstrinn8': 8,
    'aarstrinn9': 9,
    'aarstrinn10': 10,
    'vg1': 11,
    'vg2': 12,
    'vg3': 13,
}


def get_memberships_from_feide(tokens):
    from ki import models  # Avoid circular import

    if not (tokens):
        return None

    # get user's grups from dataporten
    groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
    headers = {"Authorization": "Bearer " + tokens['access_token']}
    groupinfo_response = requests.get(
        groupinfo_endpoint,
        headers=headers
    )
    if groupinfo_response.status_code == 401:
        return None
    return groupinfo_response.json()


def get_memberships_from_db(username):
    from ki import models  # Avoid circular import

    user = models.ExternalUser.objects.filter(username=username).first()
    if user:
        memberships = user.memberships if user.memberships else None
    return memberships


def get_external_userinfo(username):
    from ki import models  # Avoid circular import

    user = models.ExternalUser.objects.filter(username=username).first()
    if user:
        return {
            "username": user.username,
            "name": user.name,
            "has_self_service": user.has_self_service
        }
    return None


def get_memberships(username, login_method, tokens):
    from ki import models  # Avoid circular import

    schools = []
    levels = []
    groups = []
    employee = False
    feide_realm = os.environ.get('FEIDE_REALM', 'feide.osloskolen.no')

    if login_method == 'feide':
        # get user's memberships from feide
        groupinfo_response = get_memberships_from_feide(tokens)
        # print(f"get_memberships: {groupinfo_response}")
        if not groupinfo_response:
            return None
    elif login_method == 'local':
        # get user's memberships from database
        groupinfo_response = get_memberships_from_db(username)
        if not groupinfo_response:
            return None
    # get user's schools and levels and groups
    for group in groupinfo_response:
        # role empoyee from parent org
        if (group.get('id') == f"fc:org:{feide_realm}" and
                group['membership']['primaryAffiliation'] == "employee"):
            employee = True
        # school org_nr(s) from child org(s)
        if (group.get('type') == "fc:org" and
                group.get("parent") == f"fc:org:{feide_realm}"):
            # fifth part of id is org_nr
            org_nr = group['id'].split(":")[4]
            school = models.School.objects.get(org_nr=org_nr)
            if school:
                schools.append(school.org_nr)
        # level(s) from grep
        if (group.get('type') == "fc:grep" and
                group.get('grep_type') == "aarstrinn"):
            levels.append(group['code'])
        # education groups
        if (group.get('type') == "fc:gogroup"):
            org_nr = group['parent'].split(":")[4]
            school = models.School.objects.get(org_nr=org_nr)
            # only add groups from schools that are open for students
            if school and school.access in ['all', 'levels']:
                groups.append({
                    'id': group.get('id'),
                    'display_name': group.get('displayName'),
                    'go_type': group.get('go_type'),
                })

    return {
        'employee': employee,
        'schools': schools,
        'levels': levels,
        'groups': groups,
    }


def has_school_access(feide_memberships) -> bool:
    from ki import models  # Avoid circular import

    employee = feide_memberships.get('employee', False)
    schools = feide_memberships.get('schools', [])
    levels = feide_memberships.get('levels', [])

    for org_nr in schools:
        school = models.School.objects.filter(org_nr=org_nr).first()
        if employee:
            if school.access in ['emp', 'all', 'levels']:
                return True
        else:
            if school.access == 'all':
                return True
            elif school.access == 'levels':
                for line in school.school_accesses.all():
                    if line.level in levels:
                        return True
    return False


def is_subject_access_valid(subject_access) -> bool:
    if subject_access.valid_to < datetime.now(timezone.utc):
        subject_access.delete()
        return False
    elif subject_access.valid_from > datetime.now(timezone.utc):
        return False
    return True


def get_users_bots(username, feide_memberships):
    from ki import models  # Avoid circular import

    bots: set = set()
    employee = feide_memberships.get('employee', False)
    schools = feide_memberships.get('schools', [])
    levels = feide_memberships.get('levels', [])
    groups = feide_memberships.get('groups', [])

    # bots from subject (for students)
    if not employee:
        for group in groups:
            subject_accesses = models.SubjectAccess.objects.filter(subject_id=group['id'])
            for subject_access in subject_accesses:
                if is_subject_access_valid(subject_access):
                    bots.add(subject_access.bot_id_id)

    # bots from school
    for school in schools:
        bot_accesses = models.BotAccess.objects.filter(school_id=school)
        for bot_access in bot_accesses:
            access = False
            match bot_access.access:
                case 'all':
                    access = True
                case 'emp':
                    if employee:
                        access = True
                case 'levels':
                    if employee:
                        access = True
                    else:
                        for level in bot_access.levels.all():
                            if level.level in levels:
                                access = True
            if access:
                bots.add(bot_access.bot_id_id)

    # bots from personal bots (for employees)
    if employee:
        personal_bots = models.Bot.objects.filter(owner=username)
        for personal_bot in personal_bots:
            bots.add(personal_bot.uuid)

    return list(bots) if bots else []


def generate_group_access_list(groups=None, bot=None):
    group_list = []
    default_lifespan = get_setting('default_lifespan')
    access_dict = {}
    if bot is not None:
        for subj in bot.subjects.all():
            if subj.valid_to and (subj.valid_to < datetime.now(timezone.utc)):
                subj.delete()
                continue
            access_dict[subj.subject_id] = {
                'valid_from': subj.valid_from,
                'valid_to': subj.valid_to,
            }
    for group in groups:
        valid_from = None
        valid_to = None
        checked = False
        group_id = group.get('id')
        if group_id in access_dict:
            valid_from = access_dict[group_id].get('valid_from', None)
            valid_to = access_dict[group_id].get('valid_to', None)
            checked = True
        else:
            valid_from = datetime.now(timezone.utc)
            valid_to = (datetime.now(timezone.utc) + timedelta(days=default_lifespan))
            checked = False
        group_list.append({
            'id': group_id,
            'displayName': group.get('display_name'),
            'goType': group.get('go_type'),
            'checked': checked,
            'validRange': [valid_from, valid_to],
        })
    return group_list


def get_user_data_from_userinfo(request):
    # role
    role = 'student'
    role = 'employee' if request.userinfo.get('employee', False) else role
    role = 'admin' if request.userinfo.get('admin', False) else role
    # level
    level = None
    if (levels := request.userinfo.get('levels', None)) and role == 'student':
        level = min([aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])
    # schools
    schools = request.userinfo.get('schools', [])
    return level, schools, role


def get_admin_memberships_and_bots(username) -> dict:
    from ki import models  # Avoid circular import
    bots: set = set()
    personal_bots = models.Bot.objects.filter(owner=username)
    bots.update((bot.uuid for bot in personal_bots))
    library_bots = models.Bot.objects.filter(library=True)
    bots.update((bot.uuid for bot in library_bots))
    return {
        'admin': True,
        'employee': False,
        'schools': [],
        'levels': [],
        'groups': [],
        'bots': list(bots) if bots else [],
    }


async def use_log(bot_uuid, role=None, level=None, schools=[], message_length=1, interaction_type='text'):
    from ki import models  # Avoid circular import
    log_line = models.UseLog(
        bot_id=bot_uuid, role=role, level=level, message_length=message_length,
        interaction_type=interaction_type)
    await log_line.asave()

    for school in schools:
        # school can be of both type dict or models.School
        school_id = school.get('org_nr') if isinstance(school, dict) else school.org_nr
        if school_id:
            await models.LogSchool(school_id_id=school_id, log_id_id=log_line.id).asave()


def get_setting(setting_key, default=None):
    from ki import models  # Avoid circular import
    try:
        setting = models.Setting.objects.get(setting_key=setting_key)
    except models.Setting.DoesNotExist:
        return default
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


async def get_setting_async(setting_key):
    from ki import models  # Avoid circular import
    setting = await models.Setting.objects.aget(setting_key=setting_key)
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


def convert_to_slug(text):
    text = text.lower()
    replacements = (
        (' ', '-'),
        ('æ', 'ae'),
        ('ø', 'o'),
        ('å', 'a')
    )
    for old, new in replacements:
        text = text.replace(old, new)

    # Remove all characters invalid in a slug
    text = re.sub(r'[^-\w]', '', text)

    return text


def has_page_access(request, page):
    if page.accessable_by == 'all'\
            or request.userinfo.get('admin', False) \
            or request.userinfo.get('employee', False) \
            or (page.accessable_by == 'stud' and not request.userinfo.get('username', False)):
        return True
    return False
