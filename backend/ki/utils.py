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


def load_feide_memberships_to_request(request) -> None:
    from ki import models # Avoid circular import

    schools = []
    levels = []
    groups = []
    employee = False

    if not (tokens := request.session.get('user.auth', False)):
        request.session.clear()
        request.g.clear()
        return
    # get user's grups from dataporten
    groupinfo_endpoint = "https://groups-api.dataporten.no/groups/me/groups"
    headers = {"Authorization": "Bearer " + tokens['access_token']}
    groupinfo_response = requests.get(
        groupinfo_endpoint, 
        headers=headers
        )
    if groupinfo_response.status_code == 401:
        request.session.clear()
        request.g.clear()
        return
    groupinfo_response = groupinfo_response.json()

    # get user's schools and levels and groups
    for group in groupinfo_response:
        # role empoyee from parent org
        if (group.get('id') == "fc:org:feide.osloskolen.no" and
                group['membership']['primaryAffiliation'] == "employee"):
            employee = True
        # school org_nr(s) from child org(s)
        if (group.get('type') == "fc:org" and
                group.get("parent") == "fc:org:feide.osloskolen.no"):
            # fifth part of id is org_nr
            org_nr = group['id'].split(":")[4]
            school = models.School.objects.get(org_nr=org_nr)
            if school:
                schools.append(school)
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

    request.g['employee'] = employee
    request.g['schools'] = schools
    request.g['levels'] = levels
    request.g['groups'] = groups
    request.g['admin'] = False
    return 


def has_school_access(request) -> bool:
    schools = request.g['schools']
    levels = request.g['levels']
    employee = request.g['employee']
    for school in schools:
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


def is_subject_access_valid (subject_access) -> bool:
    if subject_access.valid_to < datetime.now(timezone.utc):
        subject_access.delete()
        return False
    elif subject_access.valid_from > datetime.now(timezone.utc):
        return False
    return True
    

def load_users_bots_to_g(request) -> None:
    from ki import models # Avoid circular import

    bots:set = set()
    allow_groups = bool(get_setting('allow_groups'))
    allow_personal = bool(get_setting('allow_personal'))
    employee = request.g['employee']
    schools = request.g['schools']
    levels = request.g['levels']
    groups = request.g['groups']
    username = request.session.get('user.username', None)

    # bots from subject
    if allow_groups and not employee:
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
                                
    # bots from personal
    if allow_personal:
        personal_bots = models.Bot.objects.filter(owner=username)
        for personal_bot in personal_bots:
            bots.add(personal_bot.uuid)

    request.g['bots'] = list(bots) if bots else []
    return


def get_groups_from_g(request, bot=None):
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
    groups = request.g['groups']
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
            'display_name': group.get('display_name'),
            'go_type': group.get('go_type'),
            'checked': checked,
            'valid_range': [valid_from, valid_to],
        })
    return group_list


def get_user_data_from_g(request):
    # role
    role = 'student'
    role = 'employee' if request.g.get('employee', False) else role
    role = 'admin' if request.g.get('admin', False) else role
    # level
    level = None
    if (levels := request.g.get('levels', None)) and role == 'student':
        level = min([ aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])
    # schools
    schools = request.g.get('schools', [])
    return level, schools, role


def admin_memberships_and_bots_to_g(request) -> None:
    from ki import models # Avoid circular import
    bots:set = set()
    username = request.session.get('user.username', None)
    personal_bots = models.Bot.objects.filter(owner=username)
    bots.update((bot.uuid for bot in personal_bots))
    library_bots = models.Bot.objects.filter(library = True)
    bots.update((bot.uuid for bot in library_bots))
    request.g['bots'] = list(bots) if bots else []
    request.g['admin'] = True
    request.g['employee'] = False
    request.g['schools'] = []
    request.g['levels'] = []
    request.g['groups'] = []
    return


async def use_log(bot_uuid, role=None, level=None, schools=[], message_length=1, interaction_type='text'):
    from ki import models # Avoid circular import
    log_line = models.UseLog(bot_id=bot_uuid, role=role, level=level, message_length=message_length, interaction_type=interaction_type)
    await log_line.asave()

    for school in schools:
        # school can be of both type dict or models.School
        school_id = school.get('org_nr') if isinstance(school, dict) else school.org_nr
        if school_id:
            await models.LogSchool(school_id_id=school_id, log_id_id=log_line.id).asave()


def get_setting(setting_key):
    from ki import models # Avoid circular import
    setting = models.Setting.objects.get(setting_key=setting_key)
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


async def get_setting_async(setting_key):
    from ki import models # Avoid circular import
    setting = await models.Setting.objects.aget(setting_key=setting_key)
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val


