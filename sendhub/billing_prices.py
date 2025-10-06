from typing import TypeAlias

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE

ValueType: TypeAlias = bool | int | float | str | list["ValueType"] | dict[str, "ValueType"]
CustomDict: TypeAlias = dict[str, ValueType]

class BillingPrices(APIResource):
    """Class representing Billing Plans"""
    @staticmethod
    def get_base_url():
        """To get the base url for the BillingPlans API"""
        return BILLING_BASE

    def list_prices(self, with_hidden=True, active_status='all'):
        """To list the price"""
        return self.get_list(with_hidden='1' if with_hidden else '0', active_status=active_status)

    def get_price(self, price_id):
        """To get a price"""
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
        currency:  str,
        productId: int,
        interval: str,
        priceMetadata: CustomDict | None = None,
        ):
        """To create a price"""
        return self.create_object(
            unitAmount = unitAmount,
            costPerText = costPerText,
            voicePricePerMinute = voicePricePerMinute,
            messageOveragePrice = messageOveragePrice,
            active = active,
            hidden = hidden,
            name = name,
            stripeNickname = stripeNickname,
            currency = currency,
            priceMetadata = priceMetadata,
            productId = productId,
            interval = interval
            )

    def update_price(self, price_id, active):
        """To update the price"""
        return self.update_object(obj_id=price_id, id=price_id, active=active)

    def delete_price(self, price_id):
        """To delete a price"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(price_id))
        requestor.request('delete', url)

    @classmethod
    def class_url(cls):
        """Returns the class url of BillingPlans"""
        return "/api/v2/prices"
