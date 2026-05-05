from unittest.mock import patch

import pytest

from sendhub.stripe_prices import StripePrice


class DummyStripePrice(StripePrice):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def stripe_price():
    return DummyStripePrice()


def test_class_url():
    assert StripePrice.class_url() == "/api/v2/stripe-prices"


def test_get_base_url():
    assert StripePrice.get_base_url() == StripePrice.get_base_url()


@patch("sendhub.stripe_prices.APIRequestor")
def test_get_price_without_expand(mock_api_requestor, stripe_price):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "price_123", "unit_amount": 2000}

    result = stripe_price.get_price("price_123")

    assert result is stripe_price
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/stripe-prices/price_123", None
    )
    assert stripe_price._refreshed == {"id": "price_123", "unit_amount": 2000}


@patch("sendhub.stripe_prices.APIRequestor")
def test_get_price_with_expand(mock_api_requestor, stripe_price):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "price_123", "product": {"id": "prod_abc"}}

    result = stripe_price.get_price("price_123", expand="product")

    assert result is stripe_price
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/stripe-prices/price_123", {"expand": "product"}
    )
