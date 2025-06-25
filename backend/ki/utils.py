import requests
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
    from ki import models # Avoid circular import

    schools = []
    levels = []
    groups = []
    is_employee = False

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
    groupinfo_response = groupinfo_response.json()

    # get user's schools and levels and groups
    for group in groupinfo_response:
        # role empoyee from parent org
        if (group.get('id') == "fc:org:feide.osloskolen.no" and
                group['membership']['primaryAffiliation'] == "employee"):
            is_employee = True
        # school org_nr(s) from child org(s)
        if (group.get('type') == "fc:org" and
                group.get("parent") == "fc:org:feide.osloskolen.no"):
            # fifth part of id is org_nr
            org_nr = group['id'].split(":")[4]
            school = models.School.objects.filter(org_nr=org_nr).first()
            if school:
                schools.append(school)
        # level(s) from grep
        if (group.get('type') == "fc:grep" and
                group.get('grep_type') == "aarstrinn"):
            levels.append(group['code'])
        # education groups
        if (group.get('type') == "fc:gogroup"):
            org_nr = group['parent'].split(":")[4]
            school = models.School.objects.filter(org_nr=org_nr).first()
            # only add groups from schools that are open for students
            if school and school.access in ['all', 'levels']:
                groups.append({
                    'id': group.get('id'),
                    'display_name': group.get('displayName'),
                    'go_type': group.get('go_type'),
                })

    return {
        'is_employee': is_employee,
        'schools': schools,
        'levels': levels,
        'groups': groups,
    }


def has_school_access(feide_memberships) -> bool:

    is_employee = feide_memberships.get('is_employee', False)
    schools = feide_memberships.get('schools', [])
    levels = feide_memberships.get('levels', [])

    for school in schools:
        if is_employee:
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


def is_subject_access_valid (subject_access) -> bool:
    if subject_access.valid_to < datetime.now(timezone.utc):
        subject_access.delete()
        return False
    elif subject_access.valid_from > datetime.now(timezone.utc):
        return False
    return True
    

def get_users_bots(username, feide_memberships):
    from ki import models # Avoid circular import

    bots:set = set()
    is_employee:bool = feide_memberships.get('is_employee', False)
    schools:list[models.School] = feide_memberships.get('schools', [])
    levels:list[str] = feide_memberships.get('levels', [])
    groups:list[str] = feide_memberships.get('groups', [])

    # bots from subject (for students)
    if not is_employee:
        for group in groups:
            subject_accesses = models.SubjectAccess.objects.filter(subject_id=group['id'])
            for subject_access in subject_accesses:
                if is_subject_access_valid(subject_access):
                    bots.add(subject_access.bot)

    # bots from school
    for school in schools:
        bot_accesses = school.accesses.filter(access__in=['all', 'emp', 'levels']).all()
        for bot_access in bot_accesses:
            access = False
            match bot_access.access:
                case 'all':
                    access = True
                case 'emp':
                    if is_employee:
                        access = True
                case 'levels':
                    if is_employee:
                        access = True
                    else:
                        for level in bot_access.levels.all():
                            if level.level in levels:
                                access = True
            if access:
                bots.add(bot_access.bot)
                                
    # bots from personal bots (for employees)
    if is_employee:
        personal_bots = models.Bot.objects.filter(owner=username).all()
        bots = bots | set(personal_bots)
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
            valid_to =  access_dict[group_id].get('valid_to', None)
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


def get_user_log_data_from_userinfo(request):
    # role
    role = 'student'
    role = 'employee' if request.userinfo.get('is_employee', False) else role
    role = 'admin' if request.userinfo.get('is_admin', False) else role
    # level
    level = None
    if (levels := request.userinfo.get('levels', None)) and role == 'student':
        level = min([ aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])
    # schools
    schools = [ school.org_nr for school in request.userinfo.get('schools', [])]
    return level, schools, role


def get_admin_memberships_and_bots(username) -> dict:
    from ki import models # Avoid circular import
    bots:set = set()
    personal_bots = set(models.Bot.objects.filter(owner=username).all())
    if personal_bots:
        bots = personal_bots
    library_bots = set(models.Bot.objects.filter(is_library_bot = True).all())
    if library_bots:
        bots = bots.union(library_bots)
    return {
        'is_admin': True,
        'is_employee': False,
        'schools': [],
        'levels': [],
        'groups': [],
        'bots': list(bots) if bots else [],
    }


async def use_log(bot_id, role=None, level=None, schools=[], message_length=1, interaction_type='text'):
    from ki import models # Avoid circular import
    use_log = models.UseLog(bot_id=bot_id, role=role, level=level, message_length=message_length, interaction_type=interaction_type)
    await use_log.asave()

    for school_id in schools:
        await models.LogSchool(school=school_id, use_log=use_log).asave()


def get_setting(setting_key):
    from ki import models # Avoid circular import
    setting = models.Setting.objects.filter(setting_key=setting_key).first()
    if not setting:
        raise AttributeError(f"Setting '{setting_key}' does not exist.")
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


async def get_setting_async(setting_key):
    from ki import models # Avoid circular import
    setting = await models.Setting.objects.filter(setting_key=setting_key).afirst()
    if not setting:
        raise AttributeError(f"Setting '{setting_key}' does not exist.")
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


