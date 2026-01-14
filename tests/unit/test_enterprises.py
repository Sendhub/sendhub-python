import pytest

from sendhub.enterprises import Enterprise


class DummyEnterprise(Enterprise):
    def get_object(self, enterprise_id):
        return {"id": enterprise_id}

@pytest.fixture
def enterprise():
    return DummyEnterprise()

def test_get_base_url():
    assert Enterprise.get_base_url() == Enterprise.get_base_url()

def test_class_url():
    # class_name() is inherited from APIResource, so we simulate its output
    class CustomEnterprise(DummyEnterprise):
        @classmethod
        def class_name(cls):
            return "enterprise"
    assert CustomEnterprise.class_url() == "/api/v3/enterprises"

def test_get_enterprise_success(enterprise):
    result = enterprise.get_enterprise(123)
    assert result == {"id": 123}

def test_get_enterprise_none(enterprise):
    with pytest.raises(ValueError):
        enterprise.get_enterprise(None)

