from unittest.mock import patch

import pytest
from sendhub.payment_methods import PaymentMethod


class DummyPaymentMethod(PaymentMethod):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def payment_method():
    return DummyPaymentMethod()


def test_class_url():
    assert PaymentMethod.class_url() == "/api/v2/payment-methods"


def test_get_base_url():
    assert PaymentMethod.get_base_url() == PaymentMethod.get_base_url()


@patch("sendhub.payment_methods.APIRequestor")
def test_attach(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {
        "id": "pm_abc",
        "customer": "cus_abc",
    }

    result = payment_method.attach("cus_abc", "pm_abc")

    assert result is payment_method
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/payment-methods/attach",
        {
            "customer_id": "cus_abc",
            "payment_method_id": "pm_abc",
            "correlation_id": "",
        },
    )
    assert payment_method._refreshed == {"id": "pm_abc", "customer": "cus_abc"}


@patch("sendhub.payment_methods.APIRequestor")
def test_attach_with_correlation_id(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "pm_abc"}

    payment_method.attach("cus_abc", "pm_abc", correlation_id="corr-123")

    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/payment-methods/attach",
        {
            "customer_id": "cus_abc",
            "payment_method_id": "pm_abc",
            "correlation_id": "corr-123",
        },
    )


@patch("sendhub.payment_methods.APIRequestor")
def test_list(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"payment_methods": [{"id": "pm_abc", "is_default": True}]}

    result = payment_method.list("cus_abc")

    assert result == [{"id": "pm_abc", "is_default": True}]
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/payment-methods/list",
        {"customer_id": "cus_abc"},
    )


@patch("sendhub.payment_methods.APIRequestor")
def test_list_with_correlation_id(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"payment_methods": []}

    payment_method.list("cus_abc", correlation_id="corr-123")

    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/payment-methods/list",
        {"customer_id": "cus_abc", "correlation_id": "corr-123"},
    )


@patch("sendhub.payment_methods.APIRequestor")
def test_detach(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"payment_methods": [{"id": "pm_1"}]}

    result = payment_method.detach("cus_abc", "pm_abc")

    assert result is payment_method
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/payment-methods/detach",
        {"customer_id": "cus_abc", "payment_method_id": "pm_abc", "correlation_id": ""},
    )
    assert payment_method._refreshed == {"payment_methods": [{"id": "pm_1"}]}


@patch("sendhub.payment_methods.APIRequestor")
def test_set_default(mock_api_requestor, payment_method):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"payment_methods": [{"id": "pm_abc", "is_default": True}]}

    result = payment_method.set_default("cus_abc", "pm_abc")

    assert result is payment_method
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/payment-methods/set-default",
        {"customer_id": "cus_abc", "payment_method_id": "pm_abc", "correlation_id": ""},
    )
    assert payment_method._refreshed == {"payment_methods": [{"id": "pm_abc", "is_default": True}]}
