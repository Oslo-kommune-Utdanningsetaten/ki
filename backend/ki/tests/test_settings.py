import pytest
from ki.utils import get_setting
from ki.models import Setting


@pytest.fixture
def sample_text_setting(db, request):
    value = getattr(request, 'param', 0)
    setting = Setting.objects.create(
        setting_key='test_text_setting',
        label='Test Text Setting',
        is_txt=True,
        txt_val=value
    )
    return setting


@pytest.fixture
def sample_int_setting(db, request):
    value = getattr(request, 'param', 42)
    setting = Setting.objects.create(
        setting_key='test_int_setting', 
        label='Test Int Setting',
        is_txt=False,
        int_val=value
    )
    return setting


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize('sample_text_setting', ['xyzzy'], indirect=True)
def test_get_text_setting(sample_text_setting):
    """Test getting a text setting value"""
    assert get_setting('test_text_setting') == 'xyzzy'


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize('sample_int_setting', [42], indirect=True)
def test_get_int_setting(sample_int_setting):
    """Test getting an integer setting value"""
    assert get_setting('test_int_setting') == 42


@pytest.mark.django_db(reset_sequences=True)
def test_get_nonexistent_setting():
    """Test getting a setting that doesn't exist raises exception"""
    with pytest.raises(Setting.DoesNotExist):
        get_setting('nonexistent_setting')
