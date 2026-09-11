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

    def get_expiring_subscriptions(
        self, period_end_gte: int, period_end_lte: int, status: str = "active"
    ) -> list[object]:
        """List subscriptions (account-wide) whose current_period_end falls
        within [period_end_gte, period_end_lte] (Unix timestamps, inclusive).

        A single filtered Stripe query, not one call per customer — use this
        instead of calling get_subscriptions() in a per-customer loop when
        the goal is "which subscriptions are expiring soon".

        Args:
            period_end_gte: Inclusive lower bound (Unix timestamp) for current_period_end.
            period_end_lte: Inclusive upper bound (Unix timestamp) for current_period_end.
            status: Stripe subscription status filter (default "active").
        Returns:
            List[object]: List of subscription objects.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        params: dict[str, Any] = {
            "period_end_gte": period_end_gte,
            "period_end_lte": period_end_lte,
            "status": status,
        }
        response = requestor.request("get", f"{self.class_url()}/expiring", params)
        if isinstance(response, list):
            return response
        return list(response)

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_end: int | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> "StripeSubscription":
        """Create a new Stripe subscription for an existing customer.

        Idempotent per (customer_id, price_id) on billing's side -- if an
        active/trialing subscription already exists at this price, it's
        returned as-is instead of creating a duplicate.

        Args:
            customer_id: The Stripe customer identifier.
            price_id: Billing service price ID (billing.price.id).
            trial_end: Optional Unix timestamp to trial the subscription until.
            metadata: Optional Stripe subscription metadata (e.g. to tag a
                secondary/add-on subscription like AI Credits, distinct from
                the account's main plan subscription).
            correlation_id: Caller-supplied trace identifier.
        Returns:
            StripeSubscription: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload: dict[str, Any] = {
            "customer_id": customer_id,
            "price_id": str(price_id),
            "correlation_id": correlation_id,
        }
        if trial_end is not None:
            payload["trial_end"] = trial_end
        if metadata:
            payload["metadata"] = metadata
        response = requestor.request("post", "/api/v2/subscription/create", payload)
        self.refresh_from(response)
        return self

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
