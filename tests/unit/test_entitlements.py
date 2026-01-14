from unittest.mock import patch

import pytest

from sendhub.entitlements import Entitlement
from sendhub.sendhub_error import AuthorizationError, EntitlementError, InvalidRequestError


class DummyEntitlement(Entitlement):
    def instance_url(self, val):
        return f"/entitlements/{val}"

    def refresh_from(self, response):
        self._refreshed = response

@pytest.fixture
def entitlement():
    return DummyEntitlement()

def test_get_base_url():
    assert Entitlement.get_base_url() == Entitlement.get_base_url()

def test_class_url():
    # class_name() is inherited from APIResource, so we simulate its output
    class CustomEntitlement(DummyEntitlement):
        @classmethod
        def class_name(cls):
            return "entitlement"
    assert CustomEntitlement.class_url() == "/api/v3/entitlements"

@patch("sendhub.entitlements.APIRequestor")
def test_list_usage_success(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"usage": "data"}
    result = entitlement.list_usage(123)
    assert result is entitlement
    assert hasattr(result, "_refreshed")

@patch("sendhub.entitlements.APIRequestor")
def test_list_usage_failure(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.list_usage(123)

@patch("sendhub.entitlements.APIRequestor")
def test_check_success(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"check": "data"}
    result = entitlement.check(123, "action", param1="val")
    assert result is entitlement
    assert hasattr(result, "_refreshed")

@patch("sendhub.entitlements.APIRequestor")
def test_check_failure(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.check(123, "action", param1="val")

@patch("sendhub.entitlements.APIRequestor")
def test_update_success(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"update": "data"}
    entitlement.uuid = "uuid123"
    result = entitlement.update(123, "action", param1="val")
    assert result is entitlement
    assert hasattr(result, "_refreshed")
    assert entitlement._id == "uuid123"

@patch("sendhub.entitlements.APIRequestor")
def test_update_auth_error(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = AuthorizationError("auth", "dev", 401, "info")
    with pytest.raises(EntitlementError):
        entitlement.update(123, "action", param1="val")

@patch("sendhub.entitlements.APIRequestor")
def test_update_runtime_error(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.update(123, "action", param1="val")

def test_confirm_update_no_id(entitlement):
    entitlement._id = None
    # Should raise InvalidRequestError before any API call
    with pytest.raises(InvalidRequestError):
        entitlement.confirm_update()

@patch("sendhub.entitlements.APIRequestor")
def test_confirm_update_success(mock_api_requestor, entitlement):
    entitlement._id = "uuid123"
    entitlement.user_id = 1
    entitlement.action = "action"
    entitlement.uuid = "uuid456"
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"confirm": "data"}
    result = entitlement.confirm_update()
    assert result is entitlement
    assert entitlement._id == "uuid456"

@patch("sendhub.entitlements.APIRequestor")
def test_confirm_update_failure(mock_api_requestor, entitlement):
    entitlement._id = "uuid123"
    entitlement.user_id = 1
    entitlement.action = "action"
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.confirm_update()

@patch("sendhub.entitlements.APIRequestor")
def test_reset_success(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"reset": "data"}
    result = entitlement.reset(123, "action")
    assert result is entitlement
    assert hasattr(result, "_refreshed")

@patch("sendhub.entitlements.APIRequestor")
def test_reset_failure(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.reset(123, "action")

@patch("sendhub.entitlements.APIRequestor")
def test_reset_all_success(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"reset_all": "data"}
    result = entitlement.reset_all(123)
    assert result is entitlement
    assert hasattr(result, "_refreshed")

@patch("sendhub.entitlements.APIRequestor")
def test_reset_all_failure(mock_api_requestor, entitlement):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        entitlement.reset_all(123)
