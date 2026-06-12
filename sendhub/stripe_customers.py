
from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class StripeCustomer(APIResource):
    """Stripe customer lookup via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def get_customer(
        self, customer_id: str, expand: str | None = None
    ) -> "StripeCustomer":
        """Retrieve a Stripe customer by its ID.

        Args:
            customer_id: The Stripe customer identifier (e.g. ``cus_xxx``).
            expand: Optional Stripe expand parameter.
        Returns:
            StripeCustomer: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        params = {"expand": expand} if expand is not None else None
        response = requestor.request(
            "get", f"/api/v2/stripe-customers/{customer_id}", params
        )
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/stripe-customers"
