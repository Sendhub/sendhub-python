from unittest.mock import patch

import pytest
from sendhub.stripe_products import StripeProduct


class DummyStripeProduct(StripeProduct):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def stripe_product():
    return DummyStripeProduct()


def test_class_url():
    assert StripeProduct.class_url() == "/api/v2/stripe-products"


def test_get_base_url():
    assert StripeProduct.get_base_url() == StripeProduct.get_base_url()


@patch("sendhub.stripe_products.APIRequestor")
def test_get_product(mock_api_requestor, stripe_product):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "prod_abc", "name": "Pro Plan"}

    result = stripe_product.get_product("prod_abc")

    assert result is stripe_product
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/stripe-products/prod_abc"
    )
    assert stripe_product._refreshed == {"id": "prod_abc", "name": "Pro Plan"}
