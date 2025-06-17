import pytest
from django.test import RequestFactory
from ki.models import Setting, BotModel, PageText, TagCategory
from ki.views.api import app_config, bot_models, empty_bot
from unittest.mock import patch



def decorate_request(request, user_roles=[], user_groups=[]):
    request.userinfo = {'dist_to_groups': True, 'groups': user_groups}
    request.session = {'user.username': 'testuser'}
    for user_role in user_roles:
        request.userinfo[user_role] = True


@pytest.fixture
def set_up_database(db, request):
    Setting.objects.create(
        id=1,
        setting_key='default_model',
        label='Modell ved nye lærerboter',
        is_txt=False,
        int_val=1
    )
    Setting.objects.create(
        id=2,
        setting_key='default_lifespan',
        label='Standard levetid for tildeling (dager)',
        is_txt=False,
        int_val=2
    )
    Setting.objects.create(
        id=3,
        setting_key='max_lifespan',
        label='Maksimal levetid for tildeling (dager)',
        is_txt=False,
        int_val=7
    )
    BotModel.objects.create(
        id=1,
        deployment_key='gpt-4o-mini',
        display_name='GPT 4o mini',
        model_description= None,
        training_cutoff= None,
    )
    PageText.objects.create(
        id='not_public',
        title='Test title',
        text='test_text',
        is_public=False,
    )
    PageText.objects.create(
        id='public',
        title='Test public title',
        text='test_text',
        is_public=True,
    )
    TagCategory.objects.create(
        id=1,
        name='Test category',
        order=1,
    )



@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize("user_roles, expected_items", [
    ([], [{'title': 'Test public title', 'url': '/info/public'}]),
    (['is_employee'], [
        {'title': 'Test title', 'url': '/info/not_public'}, 
        {'title': 'Test public title', 'url': '/info/public'}
        ]),
    (['is_admin'], [
        {'title': 'Test title', 'url': '/info/not_public'}, 
        {'title': 'Test public title', 'url': '/info/public'}
        ]),
    ])
def test_info_page_links_endpoint(set_up_database, user_roles, expected_items):
    """info_pages endpoint returns items"""
    request = RequestFactory().get('/api/app_config')
    decorate_request(request, user_roles)
    response = app_config(request)
    assert response.status_code == 200
    assert response.data['infoPages'] == expected_items


@pytest.mark.django_db(reset_sequences=True)
def test_bot_models_endpoint(set_up_database):
    """bot_models endpoint returns models"""
    request = RequestFactory().get('/api/bot_models')
    response = bot_models(request)
    assert response.status_code == 200
    expected_bot_models = {'models': [{'modelId': 1, 'displayName': 'GPT 4o mini', 'modelDescription': None, 'trainingCutoff': None, 'deploymentId': 'gpt-4o-mini'}]}       
    assert response.data == expected_bot_models


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize("user_roles, expected_status_code, expected_response", [
    ([''], 403, ''),
    (['is_admin'], 200, 'bot'),
    (['is_employee'], 200, 'bot'),
    (['is_employee', 'author'], 200, 'bot'),
    (['is_author'], 403, ''),
])
def test_empty_bot_endpoint(set_up_database, user_roles, expected_status_code, expected_response):
    """empty_bot endpoint test access"""
    request = RequestFactory().get('/api/empty_bot')
    decorate_request(request, user_roles)
    response = empty_bot(request, '')
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.data[expected_response]

