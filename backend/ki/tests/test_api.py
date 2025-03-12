import pytest
from django.test import RequestFactory
from ki.models import Setting, BotModel
from ki.views.api import menu_items, bot_models, empty_bot
from unittest.mock import patch



def decorate_request(request, user_roles=[]):
    request.g = {'settings': {'allow_groups': True}, 'dist_to_groups': True}
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
        model_id=1,
        display_name='GPT 4o mini',
        provider='Azure'
    )


@pytest.mark.django_db(reset_sequences=True)
def test_menu_items_endpoint(set_up_database):
    """menu_items endpoint returns items"""
    request = RequestFactory().get('/api/menu_items')
    decorate_request(request)
    response = menu_items(request)
    assert response.status_code == 200

    excepted_menu_items = [{'class': '', 'title': 'Startside', 'url': '/'}]
    assert response.data['menuItems'] == excepted_menu_items


@pytest.mark.django_db(reset_sequences=True)
def test_bot_models_endpoint(set_up_database):
    """bot_models endpoint returns models"""
    request = RequestFactory().get('/api/bot_models')
    response = bot_models(request)
    assert response.status_code == 200
    expected_bot_models = {'models': [{'model_id': 1, 'display_name': 'GPT 4o mini', 'model_description': None, 'training_cutoff': None}]}
    assert response.data == expected_bot_models


@pytest.mark.django_db(reset_sequences=True)
def test_empty_bot_endpoint_denies_non_user(set_up_database):
    """empty_bot endpoint denies access if user is not logged in"""
    request = RequestFactory().get('/api/empty_bot')
    decorate_request(request)
    response = empty_bot(request, '')
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_empty_bot_endpoint_admin_response(set_up_database):
    """empty_bot endpoint returns something sane"""
    mock_groups = []
    # Avoid feide request and associated problems by mocking get_groups_from_request
    with patch('ki.views.api.get_groups_from_request', return_value=mock_groups):
        request = RequestFactory().get('/api/empty_bot')
        decorate_request(request, ['admin'])
        response = empty_bot(request, '')
        assert response.status_code == 200
        assert response.data['bot']


@pytest.mark.django_db(reset_sequences=True)
def test_empty_bot_endpoint_employee_response(set_up_database):
    """empty_bot endpoint returns something sane"""
    mock_groups = []
    # Avoid feide request and associated problems by mocking get_groups_from_request
    with patch('ki.views.api.get_groups_from_request', return_value=mock_groups):
        request = RequestFactory().get('/api/empty_bot')
        decorate_request(request, ['employee'])
        response = empty_bot(request, '')
        assert response.status_code == 200
        assert response.data['bot']


@pytest.mark.django_db(reset_sequences=True)
def test_empty_bot_endpoint_author_response(set_up_database):
    """empty_bot endpoint returns something sane"""
    mock_groups = []
    # Avoid feide request and associated problems by mocking get_groups_from_request
    with patch('ki.views.api.get_groups_from_request', return_value=mock_groups):
        request = RequestFactory().get('/api/empty_bot')
        decorate_request(request, ['author'])
        response = empty_bot(request, '')
        assert response.status_code == 403
