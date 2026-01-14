from typing import Any, List, Optional, TypeAlias, TypedDict

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE

ValueType: TypeAlias = bool | int | float | str | List[Any] | dict[str, Any]
CustomDict: TypeAlias = dict[str, ValueType]


class Price(TypedDict):
    unitAmount: int
    costPerText: float
    voicePricePerMinute: float
    messageOveragePrice: float
    active: bool
    hidden: bool
    name: str
    stripeNickname: str
    currency: str
    priceMetadata: CustomDict
    productId: int
    interval: str


class BillingProducts(APIResource):
    """
    Class representing Billing Products.
    Provides methods to create, retrieve, and list billing products.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Return the base url for the BillingProducts API.
        """
        return BILLING_BASE

    def list_products(
        self, with_hidden: bool = True, active_status: str = "all"
    ) -> List[Any]:
        """
        List the products.

        Args:
            with_hidden (bool): Whether to include hidden products.
            active_status (str): Filter by active status.
        Returns:
            List[Any]: A list of product objects.
        """
        try:
            return self.get_list(
                with_hidden="1" if with_hidden else "0", active_status=active_status
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to list products: {exc}") from exc

    def get_product(self, product_id: int) -> Any:
        """
        Retrieve a product by its ID.

        Args:
            product_id (int): The ID of the product.
        Returns:
            Any: The product object.
        """
        try:
            if product_id is None:
                raise ValueError("Product ID must be provided")
            return self.get_object(product_id)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to get product with product_id={product_id}: {exc}"
            ) from exc

    def create_product(
        self,
        name: str,
        prices: List[Price],
        hippaPlan: bool,
        shortcodeKeywords: bool,
        autoAttendant: bool,
        marketingLines: bool,
        canEnableShortcode: bool,
        dataExport: bool,
        baseMessages: int,
        baseVoiceMinutes: int,
        maxUsers: int,
        maxMessages: int,
        maxSmsRecipients: int,
        maxS2sRecipients: int,
        maxVoiceMinutes: int,
        maxConferenceLines: int,
        maxConferenceParticipants: int,
        maxApiRequests: int,
        maxBasicVmTranscriptions: int,
        maxPremiumVmTranscriptions: int,
        active: bool = True,
        description: Optional[str] = None,
        statementDescriptor: Optional[str] = None,
        productMetadata: Optional[CustomDict] = None,
        defaultPriceId: Optional[Any] = None,
        hidden: bool = True,
        mailLogo: bool = True,
    ) -> Any:
        """
        Create a product.

        Args:
            name (str): Name of the product.
            prices (List[Price]): List of price dicts.
            ... (other arguments omitted for brevity)
        Returns:
            Any: The created product object.
        """
        try:
            return self.create_object(
                active=active,
                description=description,
                name=name,
                statementDescriptor=statementDescriptor,
                productMetadata=productMetadata,
                prices=prices,
                defaultPriceId=defaultPriceId,
                hidden=hidden,
                hippaPlan=hippaPlan,
                shortcodeKeywords=shortcodeKeywords,
                autoAttendant=autoAttendant,
                marketingLines=marketingLines,
                canEnableShortcode=canEnableShortcode,
                dataExport=dataExport,
                mailLogo=mailLogo,
                baseMessages=baseMessages,
                baseVoiceMinutes=baseVoiceMinutes,
                maxUsers=maxUsers,
                maxMessages=maxMessages,
                maxSmsRecipients=maxSmsRecipients,
                maxS2sRecipients=maxS2sRecipients,
                maxVoiceMinutes=maxVoiceMinutes,
                maxConferenceLines=maxConferenceLines,
                maxConferenceParticipants=maxConferenceParticipants,
                maxApiRequests=maxApiRequests,
                maxBasicVmTranscriptions=maxBasicVmTranscriptions,
                maxPremiumVmTranscriptions=maxPremiumVmTranscriptions,
            )
        except (ValueError, TypeError, RuntimeError) as exc:
            raise RuntimeError(f"Failed to create product '{name}': {exc}") from exc

    def update_product(self, product_id, active):
        """To update the plan"""
        return self.update_object(obj_id=product_id, id=product_id, active=active)

    def delete_product(self, product_id):
        """To delete a plan"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(product_id))
        requestor.request("delete", url)

    @classmethod
    def class_url(cls):
        """Returns the class url of BillingPlans"""
        return "/api/v2/products"
