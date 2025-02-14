import pytest
from django.test import RequestFactory
from ki.utils import get_setting
from ki.models import Setting, BotModel

from ki.views.api import menu_items

def decorate_request(request):
    request.g = {}
    request.g['settings'] = {}
    request.g['settings']['allow_groups'] = True
    request.session = {'user.username': 'testuser'}


@pytest.fixture
def set_up_database(db, request):
    Setting.objects.create(
        setting_key='default_model',
        label='Modell ved nye lærerboter',
        is_txt=False,
        int_val=1
    )
    BotModel.objects.create(
        model_id=1,
        deployment_id='gpt-4o-mini',
        provider='Azure'
    )


@pytest.mark.django_db(reset_sequences=True)
def test_menu_items_endpoint(set_up_database):
    """Test that the menu_items API endpoint returns status 200"""
    request = RequestFactory().get('/api/menu_items')
    decorate_request(request)
    response = menu_items(request)
    assert response.status_code == 200