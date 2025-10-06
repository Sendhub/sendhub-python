from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class BillingPlans(APIResource):
    """Class representing Billing Plans"""
    @staticmethod
    def get_base_url():
        """To get the base url for the BillingPlans API"""
        return BILLING_BASE

    def list_plans(self, with_hidden=True, active_status='all'):
        """To list the plans"""
        return self.get_list(with_hidden='1' if with_hidden else '0', active_status=active_status)

    def get_plan(self, plan_id):
        """To get a plan"""
        return self.get_object(plan_id)

    def create_plan(
            self,
            plan_type_id,
            name,
            description,
            cost,
            max_users,
            max_messages,
            max_sms_recipients,
            max_s2s_recipients,
            shortcode_keywords,
            can_enable_shortcode,
            max_voice_minutes,
            max_conference_lines,
            max_conference_participants,
            marketing_lines,
            auto_attendant,
            max_api_requests,
            max_basic_vm_transcriptions,
            max_premium_vm_transcriptions,
            data_export,
            hippa_plan,
            mail_logo=True,
            base_messages=-1,
            base_voice_minutes=-1,
            message_overage_price=0,
            voice_price_per_minute=0
    ):
        """To create a plan"""
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
            mailLogo=mail_logo)

    def update_plan(self, plan_id, active):
        """To update the plan"""
        return self.update_object(obj_id=plan_id, id=plan_id, active=active)

    def delete_plan(self, plan_id):
        """To delete a plan"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(plan_id))
        requestor.request('delete', url)

    @classmethod
    def class_url(cls):
        """Returns the class url of BillingPlans"""
        return "/api/v2/plans"
