from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class StripeSubscription(APIResource):
    """Stripe subscription management via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def get_subscriptions(
        self, customer_id: str, expand: str | None = None
    ) -> list[object]:
        """List Stripe subscriptions for a customer.

        Args:
            customer_id: The Stripe customer identifier.
            expand: Optional Stripe expand parameter.
        Returns:
            List[object]: List of subscription objects.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        params: dict[str, Any] = {"customer_id": customer_id}
        if expand is not None:
            params["expand"] = expand
        response = requestor.request("get", self.class_url(), params)
        if isinstance(response, list):
            return response
        return list(response)

    def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str | None = None,
        quantity: int | None = None,
        cancel: bool = False,
        correlation_id: str = "",
    ) -> "StripeSubscription":
        """Update or cancel a Stripe subscription.

        Args:
            subscription_id: The Stripe subscription identifier.
            new_price_id: New price ID to switch to (optional).
            quantity: New seat quantity (optional).
            cancel: Set True to cancel the subscription.
            correlation_id: Caller-supplied trace identifier.
        Returns:
            StripeSubscription: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload: dict[str, Any] = {
            "subscription_id": subscription_id,
            "cancel": cancel,
            "correlation_id": correlation_id,
        }
        if new_price_id is not None:
            payload["new_price_id"] = new_price_id
        if quantity is not None:
            payload["quantity"] = quantity
        response = requestor.request("post", "/api/v2/subscription/update", payload)
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/stripe-subscriptions"
