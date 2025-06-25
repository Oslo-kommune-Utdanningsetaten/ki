import pytest
from ki.utils import get_users_bots
from ki.models import Bot, BotAccess, BotLevel, School, SubjectAccess


@pytest.fixture
def set_up_database(db, request):
    Bot.objects.create(
        id='personal-bot-uuid',
        title='Personal Bot',
        owner='testuser',
    )
    Bot.objects.create(
        id='never-bot-uuid',
        title='never Bot',
        owner='differentuser',
    )
    Bot.objects.create(
        id='emp-bot-uuid',
        title='emp Bot',
        owner='',
    )
    Bot.objects.create(
        id='levels-bot-uuid',
        title='levels Bot',
        owner='',
    )
    Bot.objects.create(
        id='all-bot-uuid',
        title='all Bot',
        owner='',
    )
    Bot.objects.create(
        id='group-intime-bot-uuid',
        title='group Bot in time',
        owner='',
    )
    Bot.objects.create(
        id='group-outoftime-bot-uuid',
        title='group Bot out of time',
        owner='',
    )
    School.objects.create(
        id=1,
        org_nr='school-id',
        name='Test School',
        code='TS',
    )
    BotAccess.objects.create(
        bot=Bot.objects.get(id='never-bot-uuid'),
        school=School.objects.get(id=1),
        access='none',
    )
    BotAccess.objects.create(
        bot=Bot.objects.get(id='emp-bot-uuid'),
        school=School.objects.get(id=1),
        access='emp',
    )
    BotAccess.objects.create(
        bot=Bot.objects.get(id='levels-bot-uuid'),
        school=School.objects.get(id=1),
        access='levels',
    )
    BotAccess.objects.create(
        bot=Bot.objects.get(id='all-bot-uuid'),
        school=School.objects.get(id=1),
        access='all',
    )
    BotLevel.objects.create(
        bot_access=BotAccess.objects.get(bot='levels-bot-uuid', school=1),
        level='1',
    )
    BotLevel.objects.create(
        bot_access=BotAccess.objects.get(bot='never-bot-uuid', school=1),
        level='2',
    )
    SubjectAccess.objects.create(
        id=1,
        subject_id='group-id',
        bot=Bot.objects.get(id='group-intime-bot-uuid'),
        valid_from='2000-01-01 00:00 Z',
        valid_to='2099-12-31 00:00 Z',
    )
    SubjectAccess.objects.create(
        id=2,
        subject_id='group-id',
        bot=Bot.objects.get(id='group-outoftime-bot-uuid'),
        valid_from='2000-01-01 00:00 Z',
        valid_to='2000-01-01 00:01 Z',
    )


@pytest.mark.parametrize("is_employee, schools, groups, levels, expected_bots", [
    (True, [], [], [], ['personal-bot-uuid']),
    (False, [], [], [], []),
    (True, [1], [], [], ['personal-bot-uuid', 'emp-bot-uuid', 'levels-bot-uuid', 'all-bot-uuid']),
    (False, [1], [], [], ['all-bot-uuid']),
    (True, [], ['group-id'], [], ['personal-bot-uuid']),
    (False, [], ['group-id'], [], ['group-intime-bot-uuid']),
    (False, [1], [], ['1'], ['all-bot-uuid','levels-bot-uuid']),
])
def test_get_users_bots(set_up_database, is_employee, schools, groups, levels, expected_bots):
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
        'is_employee': is_employee,
        'schools': [School.objects.get(id=school) for school in schools],
        'groups': [{'id': group} for group in groups],
        'levels': levels,
    })

    assert isinstance(returned_bots, list)
    assert len(returned_bots) == len(expected_bots)
    for bot in returned_bots:
        assert bot.id in expected_bots