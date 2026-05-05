from unittest.mock import patch

import pytest

from sendhub.billing_accounts import BillingAccount


class DummyAPIResource(BillingAccount):
    def __init__(self):
        super().__init__()

    def get_object(self, enterprise_id):
        return {"id": enterprise_id}

    def create_object(self, **kwargs):
        return kwargs

    def update_object(self, obj_id, **kwargs):
        return {"obj_id": obj_id, **kwargs}

    def instance_url(self, enterprise_id):
        return f"/accounts/{enterprise_id}"

    def refresh_from(self, response):
        self._refreshed = response

@pytest.fixture
def billing_account():
    return DummyAPIResource()

def test_get_base_url():
    assert BillingAccount.get_base_url() == BillingAccount.get_base_url()

def test_get_account(billing_account):
    result = billing_account.get_account(123)
    assert result == {"id": 123}

def test_create_account(billing_account):
    result = billing_account.create_account(1, "Test", "test@example.com", 2, 5, "cust123")
    assert result["id"] == "1"
    assert result["name"] == "Test"
    assert result["planId"] == "2"
    assert result["subscriptionCount"] == 5
    assert result["customer"] == "cust123"
    assert result["billingEmail"] == "test@example.com"

def test_update_account(billing_account):
    result = billing_account.update_account(1, name="NewName", plan_id=2, subscription_count=10, plan_change_strategy="paid", billing_email="new@example.com")
    assert result["obj_id"] == 1
    assert result["name"] == "NewName"
    assert result["planId"] == "2"
    assert result["subscriptionCount"] == 10
    assert result["planChangeStrategy"] == "paid"
    assert result["billingEmail"] == "new@example.com"

def test_change_plan(billing_account):
    result = billing_account.change_plan(1, 2, plan_change_strategy="forced_fresh")
    assert result["obj_id"] == 1
    assert result["id"] == "1"
    assert result["planId"] == "2"
    assert result["planChangeStrategy"] == "forced_fresh"

@patch("sendhub.billing_accounts.APIRequestor")
def test_delete_account_success(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    billing_account.delete_account(1)
    mock_instance.request.assert_called_once()

@patch("sendhub.billing_accounts.APIRequestor")
def test_delete_account_failure(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        billing_account.delete_account(1)

@patch("sendhub.billing_accounts.APIRequestor")
def test_add_user_success(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"subscriptionCount": 1}
    result = billing_account.add_user(1, count=1)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_add_user_failure(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = ValueError("fail")
    with pytest.raises(RuntimeError):
        billing_account.add_user(1, count=1)

@patch("sendhub.billing_accounts.APIRequestor")
def test_delete_user(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    billing_account.delete_user(1)
    mock_instance.request.assert_called_once_with("delete", "/accounts/1/users")

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_payment_data(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"subscription": "data"}
    result = billing_account.get_payment_data(1)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_adjust_balance(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"balance": "adjusted"}
    result = billing_account.adjust_balance(1, 100, "credit", "desc", prorate=True, void=False)
    assert result == {"balance": "adjusted"}
    assert hasattr(billing_account, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_plan_data(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"plan": "data"}
    result = billing_account.get_plan_data(1)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_plan_history(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"history": "data"}
    result = billing_account.get_plan_history(1, 0, 10)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_invoice(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"invoice": "data"}
    result = billing_account.get_invoice(1, 2)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_create_invoice(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"invoice": "created"}
    result = billing_account.create_invoice(1, {"amount": 100})
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_charge(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"charge": "data"}
    result = billing_account.get_charge(1, 2)
    assert result is billing_account
    assert hasattr(result, "_refreshed")

@patch("sendhub.billing_accounts.APIRequestor")
def test_update_email(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"email": "updated"}
    result = billing_account.update_email(1, "new@example.com")
    assert result == {"email": "updated"}
    assert hasattr(billing_account, "_refreshed")

@patch.object(DummyAPIResource, "get_account")
@patch("sendhub.billing_accounts.APIRequestor")
def test_create_setup_intent(mock_api_requestor, mock_get_account, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "seti_123", "customer": "cus_123"}
    mock_get_account.return_value = {"customer": "cus_123"}

    result = billing_account.create_setup_intent(
        1,
        payment_method_types=["card"],
        correlation_id="corr-123",
    )

    assert result == {"id": "seti_123", "customer": "cus_123"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/setup-intents",
        {
            "customer_id": "cus_123",
            "account_id": "1",
            "payment_method_types": ["card"],
            "correlation_id": "corr-123",
        },
    )

@patch("sendhub.billing_accounts.APIRequestor")
def test_get_setup_intent(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "seti_123", "status": "requires_payment_method"}

    result = billing_account.get_setup_intent(
        "seti_123",
        enterprise_id=5,
        correlation_id="corr-456",
    )

    assert result == {"id": "seti_123", "status": "requires_payment_method"}
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/setup-intents/seti_123",
        {"account_id": "5", "correlation_id": "corr-456"},
    )

@patch.object(DummyAPIResource, "get_account")
@patch("sendhub.billing_accounts.APIRequestor")
def test_get_account_state(mock_api_requestor, mock_get_account, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {
        "has_valid_plan": True,
        "is_delinquent": False,
        "can_send_messages": True,
    }
    mock_get_account.return_value = {"customer": "cus_123"}

    result = billing_account.get_account_state(7, correlation_id="corr-789")

    assert result["can_send_messages"] is True
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/account-state/cus_123",
        {"account_id": "7", "correlation_id": "corr-789"},
    )

@patch.object(DummyAPIResource, "get_account")
def test_create_setup_intent_requires_customer_mapping(mock_get_account, billing_account):
    mock_get_account.return_value = {"id": 1}

    with pytest.raises(RuntimeError):
        billing_account.create_setup_intent(1)

def test_class_url():
    assert BillingAccount.class_url() == "/api/v2/accounts"
