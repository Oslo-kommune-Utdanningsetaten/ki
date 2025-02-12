import requests

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


def get_groups_from_request(request):
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

    if groupinfo_response.status_code == 200:
        for group in groupinfo_response.json():
            if group.get('type') == "fc:gogroup":
                subjects.append({
                    'id': group.get('id'),
                    'display_name': group.get('displayName'),
                    'go_type': group.get('go_type'),
                })
    return subjects


def get_user_data_from_request(request):
    # role
    role = 'student'
    role = 'employee' if request.g.get('employee', False) else role
    role = 'admin' if request.g.get('admin', False) else role
    # level
    level = None
    if (levels := request.g.get('levels', None)) and role == 'student':
        level = min([ aarstrinn_codes[level] for level in levels if level in aarstrinn_codes])
    # school_ids
    school_ids = [school.org_nr for school in request.g.get('schools', [])]
    return level, school_ids, role


async def use_log(bot_uuid, role=None, level=None, schools=[], message_length=1, interaction_type='text'):
    from ki import models # Avoid circular import
    log_line = models.UseLog(bot_id=bot_uuid, role=role, level=level, message_length=message_length, interaction_type=interaction_type)
    await log_line.asave()
    for school_id in schools:
        await models.LogSchool(school_id_id=school_id, log_id_id=log_line.id).asave()


def get_setting(setting_key):
    from ki import models # Avoid circular import
    setting = models.Setting.objects.get(setting_key=setting_key)
    if setting.is_txt:
        return setting.txt_val
    else:
        return setting.int_val



