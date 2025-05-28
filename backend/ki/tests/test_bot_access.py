import pytest
from ki.utils import get_users_bots
from ki.models import Bot, BotAccess, BotLevel, School, SubjectAccess


@pytest.fixture
def set_up_database(db, request):
    Bot.objects.create(
        uuid='personal-bot-uuid',
        title='Personal Bot',
        owner='testuser',
    )
    Bot.objects.create(
        uuid='never-bot-uuid',
        title='never Bot',
        owner='differentuser',
    )
    Bot.objects.create(
        uuid='emp-bot-uuid',
        title='emp Bot',
        owner='',
    )
    Bot.objects.create(
        uuid='levels-bot-uuid',
        title='levels Bot',
        owner='',
    )
    Bot.objects.create(
        uuid='all-bot-uuid',
        title='all Bot',
        owner='',
    )
    Bot.objects.create(
        uuid='group-intime-bot-uuid',
        title='group Bot in time',
        owner='',
    )
    Bot.objects.create(
        uuid='group-outoftime-bot-uuid',
        title='group Bot out of time',
        owner='',
    )
    School.objects.create(
        org_nr='school-uuid',
        school_name='Test School',
        school_code='TS',
    )
    BotAccess.objects.create(
        bot_id=Bot.objects.get(uuid='never-bot-uuid'),
        school_id=School.objects.get(org_nr='school-uuid'),
        access='none',
    )
    BotAccess.objects.create(
        bot_id=Bot.objects.get(uuid='emp-bot-uuid'),
        school_id=School.objects.get(org_nr='school-uuid'),
        access='emp',
    )
    BotAccess.objects.create(
        bot_id=Bot.objects.get(uuid='levels-bot-uuid'),
        school_id=School.objects.get(org_nr='school-uuid'),
        access='levels',
    )
    BotAccess.objects.create(
        bot_id=Bot.objects.get(uuid='all-bot-uuid'),
        school_id=School.objects.get(org_nr='school-uuid'),
        access='all',
    )
    BotLevel.objects.create(
        access_id=BotAccess.objects.get(bot_id='levels-bot-uuid', school_id='school-uuid'),
        level='1',
    )
    BotLevel.objects.create(
        access_id=BotAccess.objects.get(bot_id='never-bot-uuid', school_id='school-uuid'),
        level='2',
    )
    SubjectAccess.objects.create(
        subject_id='group-uuid',
        bot_id=Bot.objects.get(uuid='group-intime-bot-uuid'),
        valid_from='2000-01-01 00:00 Z',
        valid_to='2099-12-31 00:00 Z',
    )
    SubjectAccess.objects.create(
        subject_id='group-uuid',
        bot_id=Bot.objects.get(uuid='group-outoftime-bot-uuid'),
        valid_from='2000-01-01 00:00 Z',
        valid_to='2000-01-01 00:01 Z',
    )


@pytest.mark.parametrize("employee, schools, groups, levels, expected_bots", [
    (True, [], [], [], ['personal-bot-uuid']),
    (False, [], [], [], []),
    (True, ['school-uuid'], [], [], ['personal-bot-uuid', 'emp-bot-uuid', 'levels-bot-uuid', 'all-bot-uuid']),
    (False, ['school-uuid'], [], [], ['all-bot-uuid']),
    (True, [], ['group-uuid'], [], ['personal-bot-uuid']),
    (False, [], ['group-uuid'], [], ['group-intime-bot-uuid']),
    (False, ['school-uuid'], [], ['1'], ['all-bot-uuid','levels-bot-uuid']),
])
def test_get_users_bots(set_up_database, employee, schools, groups, levels, expected_bots):
    """ Test loading user bots into request.userinfo
        Test cases:
        employee getting personal bot
        pupil not getting personal bot
        employee getting school bots
        pupil getting school bots
        employee not getting group bots
        pupil getting group bots with access whitin time and not out of time
        pupil getting school bots with pupils level and not with another level
    """
    returned_bots = get_users_bots('testuser', {
        'employee': employee,
        'schools': schools,
        'groups': [{'id': group} for group in groups],
        'levels': levels,
    })

    assert isinstance(returned_bots, list)
    assert len(returned_bots) == len(expected_bots)
    for bot in returned_bots:
        assert bot in expected_bots