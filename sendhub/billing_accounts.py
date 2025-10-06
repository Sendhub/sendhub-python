from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class BillingAccount(APIResource):
    """Class representing Billing Account"""
    # if the user is on a paid plan then their plan change is prorated
    DEFAULT_PLAN_CHANGE_STRATEGY = 'default'

    # the user will not be charged for the plan change, the date will stay the
    # same billing date, their subscription status will be trial (to ensure
    # they stay on the same plan date)
    UNPAID_PLAN_CHANGE_STRATEGY = 'unpaid'

    # the user will be charged for the plan change, their billing date may be
    # reset, their subscription status will be active
    PAID_PLAN_CHANGE_STRATEGY = 'paid'

    # the user will be unsubscribed from their current plan and subscribed
    # a new plan
    FORCED_FRESH_PLAN = 'forced_fresh'

    @staticmethod
    def get_base_url():
        """To get the base URL for billing accounts"""
        return BILLING_BASE

    def get_account(self, enterprise_id):
        """To get the account"""
        return self.get_object(enterprise_id)

    def create_account(
            self,
            enterprise_id,
            enterprise_name,
            billing_email,
            plan_id,
            count,
            customer_id=None
    ):
        """To create a new account"""
        return self.create_object(
            id=str(enterprise_id),
            name=enterprise_name,
            planId=str(plan_id),
            subscriptionCount=count,
            customer=customer_id,
            billingEmail=billing_email)

    def delete_account(self, enterprise_id):
        """Delete account"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(enterprise_id))
        requestor.request('delete', url)

    def update_account(
            self,
            enterprise_id,
            name=None,
            plan_id=None,
            subscription_count=None,
            plan_change_strategy=None,
            billing_email=None):
        """To update the account"""
        params = {
            'id': str(enterprise_id)
        }

        if name is not None:
            params['name'] = name
        if plan_id is not None:
            params['planId'] = str(plan_id)
        if subscription_count is not None:
            params['subscriptionCount'] = subscription_count
        if billing_email is not None:
            params['billingEmail'] = billing_email
        if plan_change_strategy is not None:
            params['planChangeStrategy'] = plan_change_strategy

        return self.update_object(obj_id=enterprise_id, **params)

    def change_plan(self, enterprise_id, plan_id, plan_change_strategy=None):
        """To change a plan"""
        params = {}
        if plan_change_strategy is not None:
            params['planChangeStrategy'] = plan_change_strategy

        return self.update_object(obj_id=enterprise_id, id=str(enterprise_id), planId=str(plan_id), **params)

    def add_user(self, enterprise_id, count=1):
        """Add a user to the enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/users"
        response = requestor.request('post', url, {'subscriptionCount': count})
        self.refresh_from(response)

        return self

    def delete_user(self, enterprise_id):
        """Deletes a user"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/users"
        requestor.request('delete', url)

    def get_payment_data(self, enterprise_id):
        """To get the payment data for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/subscription"
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def adjust_balance(
            self,
            enterprise_id,
            balance_adjustment,
            adjustment_type,
            description,
            prorate=False,
            void=False
    ):
        """Adjusts the balance for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/balance"
        response = requestor.request(
            'put',
            url,
            {
                'balanceAdjustment': balance_adjustment,
                'adjustmentType': adjustment_type,
                'description': description,
                'prorate': prorate,
                'void': void
            }
        )
        self.refresh_from(response)

        return response

    def get_plan_data(self, enterprise_id):
        """To get the plan data"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/plan"
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def get_plan_history(self, enterprise_id, offset, limit):
        """To get the plan history"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/plan_history"
        response = requestor.request('get', url, {'offset': offset, 'limit': limit})
        self.refresh_from(response)

        return self

    def get_invoice(self, enterprise_id, invoice_id):
        """To get the invoice"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/invoices/{}'.format(
            self.instance_url(str(enterprise_id)), invoice_id)
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def create_invoice(self, enterprise_id, data):
        """
        creates an invoice
        :param enterprise_id: enterprise_id(Account ID)
        :param data: Billing details like amount, description
        """
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/invoices"
        response = requestor.request('post', url, data)
        self.refresh_from(response)

        return self

    def get_charge(self, enterprise_id, charge_id):
        """To get the change"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/charges/{charge_id}"
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def update_email(self, enterprise_id, billing_email):
        """To update an email"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/update_email"
        response = requestor.request('put', url, {'email': billing_email})
        self.refresh_from(response)

        return response

    @classmethod
    def class_url(cls):
        """Returns a URL for the account"""
        return "/api/v2/accounts"
