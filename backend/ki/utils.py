import requests
from datetime import datetime, timedelta

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

    schools:list = [models.School]
    levels:list = [str]
    groups:list = [dict]
    employee:bool = False

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
                    'school': school,
                })

    request.g['employee'] = employee
    request.g['schools'] = schools
    request.g['levels'] = levels
    request.g['groups'] = groups
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


def load_users_bots_to_request(request) -> None:
    from ki import models # Avoid circular import

    bots:set = set()
    allow_groups = bool(get_setting('allow_groups'))
    allow_personal = bool(get_setting('allow_personal'))
    lifespan = get_setting('lifespan')
    employee = request.g['employee']
    schools = request.g['schools']
    levels = request.g['levels']
    groups = request.g['groups']
    username = request.session.get('user.username', None)

    # bots from subject
    if allow_groups and not employee:
        for group in groups:
            subject_accesses = models.SubjectAccess.objects.filter(subject_id=group)
            for subject_access in subject_accesses:
                if (subject_access.created and
                        (subject_access.created.replace(tzinfo=None) + timedelta(hours=lifespan) < datetime.now())):
                    subject_access.delete()
                else:
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
    print(request.g['bots'])
    return


def get_groups_from_request(request):
    return request.g['groups']


def get_user_data_from_request(request):
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


