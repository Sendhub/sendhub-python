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


# ---------------------------------------------------------------------------
# Cache-aware helpers
# ---------------------------------------------------------------------------

@patch("sendhub.billing_accounts.APIRequestor")
def test_cached_billing_request_200(mock_api_requestor, billing_account):
    """_cached_billing_request returns (payload, etag, False) on 200."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"id": 1}, 200, {"ETag": '"v1"'})
    payload, etag, not_modified = billing_account._cached_billing_request("get", "/some/url")
    assert payload == {"id": 1}
    assert etag == '"v1"'
    assert not_modified is False
    call_kwargs = mock_instance.request.call_args
    assert call_kwargs[1]["return_metadata"] is True
    assert call_kwargs[1].get("extra_headers") is None  # no etag → no header


@patch("sendhub.billing_accounts.APIRequestor")
def test_cached_billing_request_sends_if_none_match(mock_api_requestor, billing_account):
    """_cached_billing_request sends If-None-Match when etag is provided."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"v1"'})
    payload, etag, not_modified = billing_account._cached_billing_request(
        "get", "/some/url", etag='"v1"'
    )
    assert not_modified is True
    call_kwargs = mock_instance.request.call_args
    assert call_kwargs[1]["extra_headers"] == {"If-None-Match": '"v1"'}


@patch("sendhub.billing_accounts.APIRequestor")
def test_get_account_cached_200(mock_api_requestor, billing_account):
    """get_account_cached hits the account endpoint and returns metadata."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"id": 1}, 200, {"ETag": '"acct-v1"'})
    payload, etag, not_modified = billing_account.get_account_cached(1)
    assert not_modified is False
    assert etag == '"acct-v1"'
    called_url = mock_instance.request.call_args[0][1]
    assert "accounts" in called_url


@patch("sendhub.billing_accounts.APIRequestor")
def test_get_account_cached_304(mock_api_requestor, billing_account):
    """get_account_cached returns (None, etag, True) on 304."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"acct-v1"'})
    payload, etag, not_modified = billing_account.get_account_cached(1, etag='"acct-v1"')
    assert payload is None
    assert not_modified is True


@patch("sendhub.billing_accounts.APIRequestor")
def test_get_subscription_cached_200(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"subscription": "data"}, 200, {"ETag": '"sub-v1"'})
    payload, etag, not_modified = billing_account.get_subscription_cached(1)
    assert not_modified is False
    called_url = mock_instance.request.call_args[0][1]
    assert called_url.endswith("/subscription")


@patch("sendhub.billing_accounts.APIRequestor")
def test_get_plan_cached_200(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"plan": "data"}, 200, {"ETag": '"plan-v1"'})
    payload, etag, not_modified = billing_account.get_plan_cached(1)
    assert not_modified is False
    called_url = mock_instance.request.call_args[0][1]
    assert called_url.endswith("/plan")


@patch("sendhub.billing_accounts.APIRequestor")
def test_get_plan_history_cached_200(mock_api_requestor, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"history": []}, 200, {"ETag": '"hist-v1"'})
    payload, etag, not_modified = billing_account.get_plan_history_cached(1, offset=0, limit=10)
    assert not_modified is False
    called_url = mock_instance.request.call_args[0][1]
    assert called_url.endswith("/plan_history")
    # offset/limit forwarded as params
    called_params = mock_instance.request.call_args[0][2]
    assert called_params == {"offset": 0, "limit": 10}


@patch.object(DummyAPIResource, "get_account")
@patch("sendhub.billing_accounts.APIRequestor")
def test_get_account_state_cached_200(mock_api_requestor, mock_get_account, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"can_send_messages": True}, 200, {"ETag": '"state-v1"'})
    mock_get_account.return_value = {"customer": "cus_abc"}
    payload, etag, not_modified = billing_account.get_account_state_cached(
        5, correlation_id="corr-1"
    )
    assert not_modified is False
    called_url = mock_instance.request.call_args[0][1]
    assert "account-state/cus_abc" in called_url
    called_params = mock_instance.request.call_args[0][2]
    assert called_params["account_id"] == "5"
    assert called_params["correlation_id"] == "corr-1"


@patch.object(DummyAPIResource, "get_account")
@patch("sendhub.billing_accounts.APIRequestor")
def test_get_account_state_cached_304(mock_api_requestor, mock_get_account, billing_account):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"state-v1"'})
    mock_get_account.return_value = {"customer": "cus_abc"}
    payload, etag, not_modified = billing_account.get_account_state_cached(
        5, etag='"state-v1"'
    )
    assert payload is None
    assert not_modified is True
