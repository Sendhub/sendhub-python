from unittest.mock import patch

import pytest
from sendhub.stripe_subscriptions import StripeSubscription


class DummyStripeSubscription(StripeSubscription):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def stripe_subscription():
    return DummyStripeSubscription()


def test_class_url():
    assert StripeSubscription.class_url() == "/api/v2/stripe-subscriptions"


def test_get_base_url():
    assert StripeSubscription.get_base_url() == StripeSubscription.get_base_url()


@patch("sendhub.stripe_subscriptions.APIRequestor")
def test_get_subscriptions_without_expand(mock_api_requestor, stripe_subscription):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": "sub_abc", "status": "active"}]

    result = stripe_subscription.get_subscriptions("cus_abc")

    assert result == [{"id": "sub_abc", "status": "active"}]
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/stripe-subscriptions",
        {"customer_id": "cus_abc"},
    )


@patch("sendhub.stripe_subscriptions.APIRequestor")
def test_get_subscriptions_with_expand(mock_api_requestor, stripe_subscription):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": "sub_abc"}]

    stripe_subscription.get_subscriptions("cus_abc", expand="latest_invoice")

    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/stripe-subscriptions",
        {"customer_id": "cus_abc", "expand": "latest_invoice"},
    )


@patch("sendhub.stripe_subscriptions.APIRequestor")
def test_get_subscriptions_non_list_response(mock_api_requestor, stripe_subscription):
    """Non-list responses (e.g. a Stripe list object) are coerced to list."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = iter([{"id": "sub_abc"}])

    result = stripe_subscription.get_subscriptions("cus_abc")

    assert isinstance(result, list)


@patch("sendhub.stripe_subscriptions.APIRequestor")
def test_update_subscription_minimal(mock_api_requestor, stripe_subscription):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "sub_abc", "status": "canceled"}

    result = stripe_subscription.update_subscription("sub_abc", cancel=True)

    assert result is stripe_subscription
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/subscription/update",
        {
            "subscription_id": "sub_abc",
            "cancel": True,
            "correlation_id": "",
        },
    )


@patch("sendhub.stripe_subscriptions.APIRequestor")
def test_update_subscription_full(mock_api_requestor, stripe_subscription):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "sub_abc", "status": "active"}

    stripe_subscription.update_subscription(
        "sub_abc",
        new_price_id="price_new",
        quantity=5,
        cancel=False,
        correlation_id="corr-999",
    )

    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/subscription/update",
        {
            "subscription_id": "sub_abc",
            "new_price_id": "price_new",
            "quantity": 5,
            "cancel": False,
            "correlation_id": "corr-999",
        },
    )
