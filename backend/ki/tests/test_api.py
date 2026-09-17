import pytest
from django.test import RequestFactory
from ki.models import Setting, BotModel, PageText, TagCategory
from ki.views.api import app_config, bot_models, info_page_links
from unittest.mock import patch


def decorate_request(request, user_roles=[], user_groups=[]):
    request.userinfo = {'dist_to_groups': True, 'groups': user_groups}
    request.session = {'user.username': 'testuser'}
    for user_role in user_roles:
        request.userinfo[user_role] = True


@pytest.fixture
def set_up_database(db, request):
    Setting.objects.create(
        setting_key='default_model',
        label='Modell ved nye lærerboter',
        is_txt=False,
        int_val=1
    )
    Setting.objects.create(
        setting_key='default_lifespan',
        label='Standard levetid for tildeling (dager)',
        is_txt=False,
        int_val=2
    )
    Setting.objects.create(
        setting_key='max_lifespan',
        label='Maksimal levetid for tildeling (dager)',
        is_txt=False,
        int_val=7
    )
    BotModel.objects.create(
        deployment_id='gpt-4o-mini',
        model_id=1,
        display_name='GPT 4o mini',
        model_description=None,
        training_cutoff=None,
    )
    PageText.objects.create(
        page_id='test',
        page_title='Test title',
        page_text='test_text',
        accessable_by=PageText.AccessEnum.EMPLOYEE,
    )
    PageText.objects.create(
        page_id='test_p',
        page_title='Test public title',
        page_text='test_text',
        accessable_by=PageText.AccessEnum.ALL,
    )
    TagCategory.objects.create(
        category_id=1,
        category_name='Test category',
        category_order=1,
    )


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize("user_roles, expected_items", [
    ([], [{'title': 'Test public title', 'url': '/info/test_p', 'hasSeparateMenu': False}]),
    (['employee'], [
        {'title': 'Test title', 'url': '/info/test', 'hasSeparateMenu': False},
        {'title': 'Test public title', 'url': '/info/test_p', 'hasSeparateMenu': False}
    ]),
    (['admin'], [
        {'title': 'Test title', 'url': '/info/test', 'hasSeparateMenu': False},
        {'title': 'Test public title', 'url': '/info/test_p', 'hasSeparateMenu': False}
    ]),
])
def test_info_page_links_endpoint(set_up_database, user_roles, expected_items):
    """info_page_links endpoint returns items"""
    request = RequestFactory().get('/api/info_page_links/')
    decorate_request(request, user_roles)
    response = info_page_links(request)
    assert response.status_code == 200
    assert response.data['infoPageLinks'] == expected_items


@pytest.mark.django_db(reset_sequences=True)
def test_bot_models_endpoint(set_up_database):
    """bot_models endpoint returns models"""
    request = RequestFactory().get('/api/bot_models')
    response = bot_models(request)
    assert response.status_code == 200
    expected_bot_models = {'models': [{'modelId': 1, 'displayName': 'GPT 4o mini',
                                       'modelDescription': None, 'trainingCutoff': None,
                                       'deploymentId': 'gpt-4o-mini', 'isReasoningModel': False}]}
    assert response.data == expected_bot_models
