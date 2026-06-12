from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class CreditNote(APIResource):
    """Credit note operations via the billing bridge."""

    @staticmethod
    def get_base_url() -> str:
        return BILLING_BASE

    @staticmethod
    def _account_credit_notes_url(
        enterprise_id: int, credit_note_id: str | None = None
    ) -> str:
        base_url = f"/api/v2/accounts/{enterprise_id}/credit-notes"
        if credit_note_id is None:
            return base_url
        return f"{base_url}/{credit_note_id}"

    def _billing_request(
        self, meth: str, url: str, params: dict | None = None
    ) -> object:
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        return requestor.request(meth, url, params)

    def create(
        self,
        enterprise_id: int,
        invoice_id: str,
        amount: int | None = None,
        refund_amount: int | None = None,
        credit_amount: int | None = None,
        out_of_band_amount: int | None = None,
        currency: str = "usd",
        reason: str | None = None,
        memo: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> object:
        """Create a credit note for an invoice through the billing bridge."""
        payload: dict[str, Any] = {
            "invoice_id": invoice_id,
            "currency": currency,
        }
        if amount is not None:
            payload["amount"] = int(amount)
        if refund_amount is not None:
            payload["refund_amount"] = int(refund_amount)
        if credit_amount is not None:
            payload["credit_amount"] = int(credit_amount)
        if out_of_band_amount is not None:
            payload["out_of_band_amount"] = int(out_of_band_amount)
        if reason is not None:
            payload["reason"] = reason
        if memo is not None:
            payload["memo"] = memo
        if metadata is not None:
            payload["metadata"] = metadata

        return self._billing_request(
            "post",
            self._account_credit_notes_url(enterprise_id),
            payload,
        )

    def list(self, enterprise_id: int, limit: int = 10, offset: int = 0) -> object:
        """List credit notes for an enterprise account."""
        return self._billing_request(
            "get",
            self._account_credit_notes_url(enterprise_id),
            {"limit": limit, "offset": offset},
        )

    def get(self, enterprise_id: int, credit_note_id: str) -> object:
        """Retrieve a single credit note for an enterprise account."""
        return self._billing_request(
            "get",
            self._account_credit_notes_url(enterprise_id, credit_note_id),
        )

    def void(
        self,
        enterprise_id: int,
        credit_note_id: str,
        reason: str | None = None,
    ) -> object:
        """Void a credit note through the billing bridge."""
        payload = None
        if reason is not None:
            payload = {"reason": reason}

        return self._billing_request(
            "post",
            f"{self._account_credit_notes_url(enterprise_id, credit_note_id)}/void",
            payload,
        )

    @classmethod
    def class_url(cls) -> str:
        return "/api/v2/credit-notes"
