from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class Coupon(APIResource):
    """Billing bridge coupon lookup."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    def get_coupon(self, coupon_id: str) -> "Coupon":
        """Retrieve a coupon by its ID.

        Args:
            coupon_id: The coupon identifier.
        Returns:
            Coupon: self, refreshed from the response.
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        response = requestor.request("get", f"/api/v2/bridge/coupons/{coupon_id}")
        self.refresh_from(response)
        return self

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/bridge/coupons"
