from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class PaymentMethod(APIResource):
    """Stripe payment method operations via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def attach(
        self,
        customer_id: str,
        payment_method_id: str,
        correlation_id: str = "",
    ) -> "PaymentMethod":
        """Attach a payment method to a Stripe customer.

        Args:
            customer_id: The Stripe customer identifier.
            payment_method_id: The Stripe payment method identifier.
            correlation_id: Caller-supplied trace identifier.
        Returns:
            PaymentMethod: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload: dict[str, Any] = {
            "customer_id": customer_id,
            "payment_method_id": payment_method_id,
            "correlation_id": correlation_id,
        }
        response = requestor.request("post", "/api/v2/payment-methods/attach", payload)
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/payment-methods"
