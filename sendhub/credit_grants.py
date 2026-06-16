from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class CreditGrant(APIResource):
    """Credit grant operations via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    @staticmethod
    def _account_credit_grants_url(
        enterprise_id: int, credit_grant_id: str | None = None
    ) -> str:
        base = f"/api/v2/accounts/{enterprise_id}/credit-grants"
        return base if credit_grant_id is None else f"{base}/{credit_grant_id}"

    def _billing_request(self, meth: str, url: str, params: dict | None = None) -> object:
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        return requestor.request(meth, url, params)

    def create(
        self,
        enterprise_id: int,
        customer_id: str,
        amount_value: int,
        amount_currency: str = "usd",
        category: str = "promotional",
        name: str | None = None,
        expires_at: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> object:
        """Create a credit grant through the billing bridge."""
        payload: dict[str, Any] = {
            "customer_id": customer_id,
            "amount_value": int(amount_value),
            "amount_currency": amount_currency,
            "category": category,
        }
        if name is not None:
            payload["name"] = name
        if expires_at is not None:
            payload["expires_at"] = expires_at
        if metadata is not None:
            payload["metadata"] = metadata

        return self._billing_request(
            "post",
            self._account_credit_grants_url(enterprise_id),
            payload,
        )

    def list(self, enterprise_id: int, limit: int = 10, offset: int = 0) -> object:
        """List credit grants for an enterprise account."""
        return self._billing_request(
            "get",
            self._account_credit_grants_url(enterprise_id),
            {"limit": limit, "offset": offset},
        )

    def get(self, enterprise_id: int, credit_grant_id: str) -> object:
        """Retrieve a single credit grant for an enterprise account."""
        return self._billing_request(
            "get",
            self._account_credit_grants_url(enterprise_id, credit_grant_id),
        )

    def void(self, enterprise_id: int, credit_grant_id: str) -> object:
        """Void a credit grant through the billing bridge."""
        return self._billing_request(
            "post",
            f"{self._account_credit_grants_url(enterprise_id, credit_grant_id)}/void",
        )

    def expire(self, enterprise_id: int, credit_grant_id: str) -> object:
        """Expire a credit grant through the billing bridge."""
        return self._billing_request(
            "post",
            f"{self._account_credit_grants_url(enterprise_id, credit_grant_id)}/expire",
        )

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/credit-grants"
