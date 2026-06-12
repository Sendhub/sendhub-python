from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class Invoice(APIResource):
    """Stripe invoice processing via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def process(
        self,
        invoice_id: str,
        action: str,
        correlation_id: str = "",
        expected_customer_id: str | None = None,
        expected_currency: str | None = None,
    ) -> "Invoice":
        """Process a Stripe invoice action.

        Args:
            invoice_id: The Stripe invoice identifier.
            action: Action to perform (e.g. ``pay``, ``void``, ``finalize``).
            correlation_id: Caller-supplied trace identifier.
            expected_customer_id: Guard against mis-routed requests.
            expected_currency: Guard against currency mismatches.
        Returns:
            Invoice: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload: dict[str, Any] = {
            "invoice_id": invoice_id,
            "action": action,
            "correlation_id": correlation_id,
        }
        if expected_customer_id is not None:
            payload["expected_customer_id"] = expected_customer_id
        if expected_currency is not None:
            payload["expected_currency"] = expected_currency
        response = requestor.request("post", "/api/v2/invoice/process", payload)
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/invoices"
