
from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class StripePrice(APIResource):
    """
    Stripe-native price lookup via the billing bridge.
    """

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def get_price(self, price_id: str, expand: str | None = None) -> "StripePrice":
        """Retrieve a Stripe price by its ID.

        Args:
            price_id: The Stripe price identifier (e.g. ``price_xxx``).
            expand: Optional Stripe expand parameter.
        Returns:
            StripePrice: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        params = {"expand": expand} if expand is not None else None
        response = requestor.request("get", f"/api/v2/stripe-prices/{price_id}", params)
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/stripe-prices"
