from unittest.mock import patch

import sendhub
from sendhub.constants import BILLING_BASE
from sendhub.credit_grants import CreditGrant


def test_class_url():
    assert CreditGrant.class_url() == "/api/v2/credit-grants"


def test_get_base_url():
    assert CreditGrant.get_base_url() == BILLING_BASE


def test_lazy_import():
    assert sendhub.CreditGrant is CreditGrant
    assert "CreditGrant" in sendhub.__all__


def test_account_credit_grants_url_without_id():
    url = CreditGrant._account_credit_grants_url(42)
    assert url == "/api/v2/accounts/42/credit-grants"


def test_account_credit_grants_url_with_id():
    url = CreditGrant._account_credit_grants_url(42, "cg_abc")
    assert url == "/api/v2/accounts/42/credit-grants/cg_abc"


@patch("sendhub.credit_grants.APIRequestor")
def test_create_minimal(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cg_1"}
    grant = CreditGrant()

    result = grant.create(
        enterprise_id=10,
        customer_id="cus_xyz",
        amount_value=5000,
    )

    assert result == {"id": "cg_1"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/10/credit-grants",
        {
            "customer_id": "cus_xyz",
            "amount_value": 5000,
            "amount_currency": "usd",
            "category": "promotional",
        },
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_create_all_optional_fields(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cg_2"}
    grant = CreditGrant()

    result = grant.create(
        enterprise_id=10,
        customer_id="cus_xyz",
        amount_value=1000,
        amount_currency="eur",
        category="paid",
        name="Q1 Credit",
        expires_at=1800000000,
        metadata={"note": "test"},
    )

    assert result == {"id": "cg_2"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/10/credit-grants",
        {
            "customer_id": "cus_xyz",
            "amount_value": 1000,
            "amount_currency": "eur",
            "category": "paid",
            "name": "Q1 Credit",
            "expires_at": 1800000000,
            "metadata": {"note": "test"},
        },
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_create_coerces_amount_value_to_int(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {}
    grant = CreditGrant()

    grant.create(enterprise_id=1, customer_id="cus_1", amount_value=99.9)

    called_params = mock_instance.request.call_args[0][2]
    assert called_params["amount_value"] == 99
    assert isinstance(called_params["amount_value"], int)


@patch("sendhub.credit_grants.APIRequestor")
def test_create_sets_billing_base(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {}
    grant = CreditGrant()

    grant.create(enterprise_id=1, customer_id="cus_1", amount_value=100)

    requestor_instance = mock_api_requestor.return_value
    assert mock_api_requestor.return_value is requestor_instance
    # api_base is set on the requestor before the call
    assert mock_api_requestor.return_value.api_base == BILLING_BASE


@patch("sendhub.credit_grants.APIRequestor")
def test_list_defaults(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": "cg_1"}]
    grant = CreditGrant()

    result = grant.list(enterprise_id=10)

    assert result == [{"id": "cg_1"}]
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/accounts/10/credit-grants",
        {"limit": 10, "offset": 0},
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_list_custom_pagination(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = []
    grant = CreditGrant()

    grant.list(enterprise_id=10, limit=50, offset=100)

    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/accounts/10/credit-grants",
        {"limit": 50, "offset": 100},
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_get(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cg_abc"}
    grant = CreditGrant()

    result = grant.get(enterprise_id=10, credit_grant_id="cg_abc")

    assert result == {"id": "cg_abc"}
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/accounts/10/credit-grants/cg_abc",
        None,
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_void(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cg_abc", "status": "voided"}
    grant = CreditGrant()

    result = grant.void(enterprise_id=10, credit_grant_id="cg_abc")

    assert result == {"id": "cg_abc", "status": "voided"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/10/credit-grants/cg_abc/void",
        None,
    )


@patch("sendhub.credit_grants.APIRequestor")
def test_expire(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cg_abc", "status": "expired"}
    grant = CreditGrant()

    result = grant.expire(enterprise_id=10, credit_grant_id="cg_abc")

    assert result == {"id": "cg_abc", "status": "expired"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/10/credit-grants/cg_abc/expire",
        None,
    )
