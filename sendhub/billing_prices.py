from typing import TypeAlias

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE

ValueType: TypeAlias = (
    bool | int | float | str | list["ValueType"] | dict[str, "ValueType"]
)
CustomDict: TypeAlias = dict[str, ValueType]


class BillingPrices(APIResource):
    """
    Class representing Billing Prices.
    Provides methods to create, update, delete, and list billing prices.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base url for the BillingPrices API.
        """
        return BILLING_BASE

    def list_prices(
        self, with_hidden: bool = True, active_status: str = "all"
    ) -> object:
        """
        Lists billing prices.

        Args:
            with_hidden (bool): Whether to include hidden prices.
            active_status (str): Filter by active status.
        Returns:
            object: List of prices.
        """
        return self.get_list(
            with_hidden="1" if with_hidden else "0", active_status=active_status
        )

    def get_price(self, price_id: int) -> object:
        """
        Retrieves a price by ID.

        Args:
            price_id (int): The price ID.
        Returns:
            object: The price object.
        """
        return self.get_object(price_id)

    def create_price(
        self,
        unitAmount: int,
        costPerText: float,
        voicePricePerMinute: float,
        messageOveragePrice: float,
        active: bool,
        hidden: bool,
        name: str,
        stripeNickname: str,
        currency: str,
        productId: int,
        interval: str,
        priceMetadata: CustomDict | None = None,
    ) -> object:
        """
        Creates a new billing price.

        Args:
            unitAmount (int): Unit amount.
            costPerText (float): Cost per text.
            voicePricePerMinute (float): Voice price per minute.
            messageOveragePrice (float): Message overage price.
            active (bool): Whether the price is active.
            hidden (bool): Whether the price is hidden.
            name (str): Name of the price.
            stripeNickname (str): Stripe nickname.
            currency (str): Currency code.
            productId (int): Product ID.
            interval (str): Billing interval.
            priceMetadata (Optional[CustomDict]): Additional metadata.
        Returns:
            object: The created price object.
        """
        return self.create_object(
            unitAmount=unitAmount,
            costPerText=costPerText,
            voicePricePerMinute=voicePricePerMinute,
            messageOveragePrice=messageOveragePrice,
            active=active,
            hidden=hidden,
            name=name,
            stripeNickname=stripeNickname,
            currency=currency,
            priceMetadata=priceMetadata,
            productId=productId,
            interval=interval,
        )

    def update_price(self, price_id: int, active: bool) -> object:
        """
        Updates the active status of a price.

        Args:
            price_id (int): The price ID.
            active (bool): New active status.
        Returns:
            object: The updated price object.
        """
        return self.update_object(obj_id=price_id, id=price_id, active=active)

    def delete_price(self, price_id: int) -> None:
        """
        Deletes a price by ID.

        Args:
            price_id (int): The price ID.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(price_id))
            requestor.request("delete", url)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to delete price with price_id={price_id}: {exc}"
            ) from exc

    @classmethod
    def class_url(cls) -> str:
        """
        Returns the class url of BillingPrices.
        """
        return "/api/v2/prices"

    def list_prices_cached(
        self,
        with_hidden: bool = True,
        active_status: str = "all",
        etag: str | None = None,
    ) -> tuple[object | None, str | None, bool]:
        """Cache-aware price list read.

        Sends ``If-None-Match: <etag>`` when *etag* is supplied.  Returns a
        3-tuple ``(prices, new_etag, not_modified)``.

        * ``prices`` – list returned by the server, or ``None`` on ``304``.
        * ``new_etag`` – value of the ``ETag`` response header, or ``None``.
        * ``not_modified`` – ``True`` when the server replied with ``304``.
        """
        extra_headers: dict[str, str] = {}
        if etag:
            extra_headers["If-None-Match"] = etag
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload, rcode, resp_headers = requestor.request(
            meth="get",
            url=self.class_url(),
            params={"with_hidden": "1" if with_hidden else "0", "active_status": active_status},
            extra_headers=extra_headers or None,
            return_metadata=True,
        )
        new_etag: str | None = resp_headers.get("ETag") or resp_headers.get("etag")
        not_modified = rcode == 304
        if not not_modified and payload is not None:
            return payload, new_etag, not_modified
        return None, new_etag, not_modified
