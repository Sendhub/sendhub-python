from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class StripeProduct(APIResource):
    """
    Stripe-native product lookup via the billing
    """

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def get_product(self, product_id: str) -> "StripeProduct":
        """Retrieve a Stripe product by its ID.

        Args:
            product_id: The Stripe product identifier (e.g. ``prod_xxx``).
        Returns:
            StripeProduct: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        response = requestor.request("get", f"/api/v2/stripe-products/{product_id}")
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/stripe-products"
