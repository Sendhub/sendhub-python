from unittest.mock import patch

import pytest

from sendhub.stripe_customers import StripeCustomer


class DummyStripeCustomer(StripeCustomer):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def stripe_customer():
    return DummyStripeCustomer()


def test_class_url():
    assert StripeCustomer.class_url() == "/api/v2/stripe-customers"


def test_get_base_url():
    assert StripeCustomer.get_base_url() == StripeCustomer.get_base_url()


@patch("sendhub.stripe_customers.APIRequestor")
def test_get_customer_without_expand(mock_api_requestor, stripe_customer):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cus_abc", "email": "user@example.com"}

    result = stripe_customer.get_customer("cus_abc")

    assert result is stripe_customer
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/stripe-customers/cus_abc", None
    )
    assert stripe_customer._refreshed == {"id": "cus_abc", "email": "user@example.com"}


@patch("sendhub.stripe_customers.APIRequestor")
def test_get_customer_with_expand(mock_api_requestor, stripe_customer):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {
        "id": "cus_abc",
        "sources": {"data": []},
    }

    result = stripe_customer.get_customer("cus_abc", expand="sources")

    assert result is stripe_customer
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/stripe-customers/cus_abc", {"expand": "sources"}
    )
