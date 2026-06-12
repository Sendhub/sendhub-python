from unittest.mock import patch

import pytest
from sendhub.profile import Profile


class DummyProfile(Profile):
    def instance_url(self, user_id):
        return f"/profile/{user_id}"

    def refresh_from(self, response):
        self._refreshed = response

    def get_object(self, user_id):
        return {"id": user_id}

@pytest.fixture
def profile():
    return DummyProfile()

def test_get_base_url():
    assert Profile.get_base_url() == Profile.get_base_url()

def test_class_url():
    class CustomProfile(DummyProfile):
        @classmethod
        def class_name(cls):
            return "profile"
    assert CustomProfile.class_url() == "/api/v3/profiles"

@patch("sendhub.profile.APIRequestor")
def test_fetch_success(mock_api_requestor, profile):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"profile": "data"}
    result = profile.fetch(123)
    assert result is profile
    assert hasattr(result, "_refreshed")

@patch("sendhub.profile.APIRequestor")
def test_fetch_failure(mock_api_requestor, profile):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        profile.fetch(123)

@patch("sendhub.profile.APIRequestor")
def test_update_success(mock_api_requestor, profile):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    result = profile.update(123, {"name": "Test"})
    assert result is profile

@patch("sendhub.profile.APIRequestor")
def test_update_failure(mock_api_requestor, profile):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        profile.update(123, {"name": "Test"})

def test_get_user(profile):
    result = profile.get_user(123)
    assert result == {"id": 123}
