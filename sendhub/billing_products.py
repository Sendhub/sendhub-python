from typing import List, TypeAlias, TypedDict

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE

ValueType: TypeAlias = bool | int | float | str | list["ValueType"] | dict[str, "ValueType"]
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
    currency:  str
    priceMetadata: CustomDict
    productId: int
    interval: str



class BillingProducts(APIResource):
    """Class representing Billing Plans"""
    @staticmethod
    def get_base_url():
        """To get the base url for the BillingPlans API"""
        return BILLING_BASE

    def list_products(self, with_hidden=True, active_status='all'):
        """To list the plans"""
        return self.get_list(with_hidden='1' if with_hidden else '0', active_status=active_status)

    def get_product(self, product_id):
        """To get a plan"""
        return self.get_object(product_id)

    def create_product(
        self,
        name: str ,
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
        description: str = None,

        statementDescriptor: str = None,
        productMetadata: CustomDict | None = None,
        defaultPriceId = None,
        hidden: bool = True,
        mailLogo: bool = True,
        ):
        """To create a product"""
        return self.create_object(
            active = active,
            description = description,
            name = name,
            statementDescriptor = statementDescriptor,
            productMetadata = productMetadata,
            prices = prices,
            defaultPriceId = defaultPriceId,
            hidden = hidden,
            hippaPlan = hippaPlan,
            shortcodeKeywords = shortcodeKeywords,
            autoAttendant = autoAttendant,
            marketingLines = marketingLines,
            canEnableShortcode = canEnableShortcode,
            dataExport = dataExport,
            mailLogo = mailLogo,
            baseMessages = baseMessages,
            baseVoiceMinutes = baseVoiceMinutes,
            maxUsers = maxUsers,
            maxMessages = maxMessages,
            maxSmsRecipients = maxSmsRecipients,
            maxS2sRecipients = maxS2sRecipients,
            maxVoiceMinutes = maxVoiceMinutes,
            maxConferenceLines = maxConferenceLines,
            maxConferenceParticipants = maxConferenceParticipants,
            maxApiRequests = maxApiRequests,
            maxBasicVmTranscriptions = maxBasicVmTranscriptions,
            maxPremiumVmTranscriptions = maxPremiumVmTranscriptions
            )

    def update_product(self, product_id, active):
        """To update the plan"""
        return self.update_object(obj_id=product_id, id=product_id, active=active)

    def delete_product(self, product_id):
        """To delete a plan"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(product_id))
        requestor.request('delete', url)

    @classmethod
    def class_url(cls):
        """Returns the class url of BillingPlans"""
        return "/api/v2/products"
