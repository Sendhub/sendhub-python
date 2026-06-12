# Standard library imports
from typing import Any

# Local imports
from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE
from sendhub.sendhub_object import SendHubObject


class CreditCardBlacklist(APIResource):
    """Class for CreditCardBlacklist"""

    @staticmethod
    def get_base_url() -> str:
        """Return the base URL."""
        return BILLING_BASE

    def list_blacklist(self, search_query: Any = None) -> list[SendHubObject]:
        """List the blacklist items."""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()

        search_url = [self.class_url()]
        if search_query:
            search_url.append(f"/{search_query}")
        url = "".join(search_url)
        response = requestor.request(meth="get", url=url, params={})
        return [SendHubObject.construct_from(i) for i in response]

    def get_blacklist_item(self, item_id: Any) -> SendHubObject:
        """Get the blacklist item."""
        if item_id is None:
            raise ValueError("item_id must not be None")
        return self.get_object(item_id)

    def create_blacklist_item(self, fingerprint: str) -> SendHubObject:
        """Create a blacklist item."""
        if not isinstance(fingerprint, str):
            raise TypeError("fingerprint must be a string")
        return self.create_object(fingerprint=fingerprint)

    def delete_blacklist_item(self, item_id: Any) -> None:
        """Delete the blacklist item."""
        if item_id is None:
            raise ValueError("item_id must not be None")
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(item_id))
        requestor.request("delete", url)

    @classmethod
    def class_url(cls) -> str:
        """Return url for the class."""
        return "/api/v2/cards/blacklist"
