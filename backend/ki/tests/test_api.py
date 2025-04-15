import pytest
from django.test import RequestFactory
from ki.models import Setting, BotModel, PageText, TagCategory
from ki.views.api import menu_items, bot_models, empty_bot
from unittest.mock import patch



def decorate_request(request, user_roles=[], user_groups=[]):
    request.g = {'settings': {'allow_groups': True}, 'dist_to_groups': True, 'groups': user_groups}
    request.session = {'user.username': 'testuser'}
    for user_role in user_roles:
        request.g[user_role] = True


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
        model_description= None,
        training_cutoff= None,
    )
    PageText.objects.create(
        page_id='test',
        page_title='Test title',
        page_text='test_text',
        public=False,
    )
    TagCategory.objects.create(
        category_id=1,
        category_name='Test category',
        category_order=1,
    )



@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize("user_roles, expected_menu_items", [
    ([], [{'class': '', 'title': 'Startside', 'url': '/'}]),
    (['employee'], [
        {'title': 'Test title', 'url': '/info/test'}, 
        {'class': '', 'title': 'Startside', 'url': '/'}
        ]),
    (['admin'], [
        {"title": "Innstillinger", "url": "/settings"},
        {'title': 'Test title', 'url': '/info/test'},
        {'class': '', 'title': 'Startside', 'url': '/'},
        ]),
    ])
def test_menu_items_endpoint(set_up_database, user_roles, expected_menu_items):
    """menu_items endpoint returns items"""
    request = RequestFactory().get('/api/menu_items')
    decorate_request(request, user_roles)
    response = menu_items(request)
    assert response.status_code == 200
    assert response.data['menuItems'] == expected_menu_items


@pytest.mark.django_db(reset_sequences=True)
def test_bot_models_endpoint(set_up_database):
    """bot_models endpoint returns models"""
    request = RequestFactory().get('/api/bot_models')
    response = bot_models(request)
    assert response.status_code == 200
    expected_bot_models = {'models': [{'model_id': 1, 'display_name': 'GPT 4o mini', 'model_description': None, 'training_cutoff': None, 'deployment_id': 'gpt-4o-mini'}]}       
    assert response.data == expected_bot_models


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize("user_roles, expected_status_code, expected_response", [
    ([''], 403, ''),
    (['admin'], 200, 'bot'),
    (['employee'], 200, 'bot'),
    (['employee', 'author'], 200, 'bot'),
    (['author'], 403, ''),
])
def test_empty_bot_endpoint(set_up_database, user_roles, expected_status_code, expected_response):
    """empty_bot endpoint test access"""
    request = RequestFactory().get('/api/empty_bot')
    decorate_request(request, user_roles)
    response = empty_bot(request, '')
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.data[expected_response]

