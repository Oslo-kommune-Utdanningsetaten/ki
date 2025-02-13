import pytest
from rest_framework.test import APIClient
from django.test import RequestFactory

from ki.views import menu_items

def decorate_request(request):
    request.g = {}
    request.g['settings'] = {}
    request.g['settings']['allow_groups'] = ['admin']


@pytest.mark.django_db
def test_menu_items_endpoint():
    """Test that the menu_items API endpoint returns status 200"""
    factory = RequestFactory()
    # Create a request and force authentication
    request = factory.get('/api/menu_items')
    decorate_request(request)
    
    # Call the view with the request
    response = menu_items(request)

    assert response.status_code == 200