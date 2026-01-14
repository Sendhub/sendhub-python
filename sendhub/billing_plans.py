from typing import Any, List

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class BillingPlans(APIResource):
    """Class representing Billing Plans"""

    @staticmethod
    def get_base_url() -> str:
        """Return the base url for the BillingPlans API."""
        return BILLING_BASE

    def list_plans(
        self, with_hidden: bool = True, active_status: str = "all"
    ) -> List[Any]:
        """List the plans."""
        return self.get_list(
            with_hidden="1" if with_hidden else "0", active_status=active_status
        )

    def get_plan(self, plan_id: Any) -> Any:
        """Get a plan by ID."""
        if plan_id is None:
            raise ValueError("plan_id must not be None")
        return self.get_object(plan_id)

    def create_plan(
        self,
        plan_type_id: Any,
        name: str,
        description: str,
        cost: Any,
        max_users: Any,
        max_messages: Any,
        max_sms_recipients: Any,
        max_s2s_recipients: Any,
        shortcode_keywords: Any,
        can_enable_shortcode: Any,
        max_voice_minutes: Any,
        max_conference_lines: Any,
        max_conference_participants: Any,
        marketing_lines: Any,
        auto_attendant: Any,
        max_api_requests: Any,
        max_basic_vm_transcriptions: Any,
        max_premium_vm_transcriptions: Any,
        data_export: Any,
        hippa_plan: Any,
        mail_logo: bool = True,
        base_messages: Any = -1,
        base_voice_minutes: Any = -1,
        message_overage_price: Any = 0,
        voice_price_per_minute: Any = 0,
    ) -> Any:
        """Create a plan."""
        return self.create_object(
            planTypeId=plan_type_id,
            name=name,
            description=description,
            cost=str(cost),
            msgOveragePrice=str(message_overage_price),
            voicePricePerMinute=str(voice_price_per_minute),
            maxUsers=str(max_users),
            baseMessages=str(base_messages),
            maxMessages=str(max_messages),
            maxSmsRecipients=str(max_sms_recipients),
            maxS2sRecipients=str(max_s2s_recipients),
            shortcodeKeywords=shortcode_keywords,
            canEnableShortcode=can_enable_shortcode,
            baseVoiceMinutes=str(base_voice_minutes),
            hippaPlan=hippa_plan,
            maxVoiceMinutes=str(max_voice_minutes),
            maxConferenceLines=str(max_conference_lines),
            maxConferenceParticipants=str(max_conference_participants),
            marketingLines=marketing_lines,
            autoAttendant=auto_attendant,
            maxApiRequests=str(max_api_requests),
            maxBasicVmTranscriptions=str(max_basic_vm_transcriptions),
            maxPremiumVmTranscriptions=str(max_premium_vm_transcriptions),
            dataExport=data_export,
            mailLogo=mail_logo,
        )

    def update_plan(self, plan_id: Any, active: bool) -> Any:
        """Update the plan."""
        if plan_id is None:
            raise ValueError("plan_id must not be None")
        return self.update_object(obj_id=plan_id, id=plan_id, active=active)

    def delete_plan(self, plan_id: Any) -> None:
        """Delete a plan."""
        if plan_id is None:
            raise ValueError("plan_id must not be None")
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(plan_id))
        requestor.request("delete", url)

    @classmethod
    def class_url(cls) -> str:
        """Return the class url of BillingPlans."""
        return "/api/v2/plans"
