from typing import Any, Optional

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import BILLING_BASE


class BillingAccount(APIResource):
    """
    Class representing a Billing Account.
    Provides methods to create, update, delete, and manage billing accounts and their plans.
    """

    DEFAULT_PLAN_CHANGE_STRATEGY: str = "default"
    UNPAID_PLAN_CHANGE_STRATEGY: str = "unpaid"
    PAID_PLAN_CHANGE_STRATEGY: str = "paid"
    FORCED_FRESH_PLAN: str = "forced_fresh"

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base URL for billing accounts.
        """
        return BILLING_BASE

    def get_account(self, enterprise_id: int) -> object:
        """
        Retrieves the billing account for a given enterprise ID.

        Args:
            enterprise_id (int): The ID of the enterprise.
        Returns:
            object: The billing account object.
        """
        return self.get_object(enterprise_id)

    def _billing_request(self, meth: str, url: str, params: Optional[dict] = None) -> object:
        """Issue a request against the billing service."""

        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        return requestor.request(meth, url, params)

    @staticmethod
    def _setup_intents_url(intent_id: Optional[str] = None) -> str:
        """Build the setup-intent endpoint path."""

        base_url = "/api/v2/setup-intents"
        if intent_id is None:
            return base_url
        return f"{base_url}/{intent_id}"

    @staticmethod
    def _account_state_url(customer_id: str) -> str:
        """Build the account-state endpoint path."""

        return f"/api/v2/account-state/{customer_id}"

    @staticmethod
    def _extract_customer_id(account: object) -> Optional[str]:
        """Read a customer id from either a dict or SendHubObject-style response."""

        getter = getattr(account, "get", None)
        if callable(getter):
            customer_id = getter("customer")
            if customer_id:
                return str(customer_id)

        customer_id = getattr(account, "customer", None)
        if customer_id:
            return str(customer_id)
        return None

    def _get_customer_id_for_enterprise(self, enterprise_id: int) -> str:
        """Resolve the Stripe customer id from the billing account response."""

        account = self.get_account(enterprise_id)
        customer_id = self._extract_customer_id(account)
        if not customer_id:
            raise RuntimeError(
                f"Billing account for enterprise_id={enterprise_id} does not expose a Stripe customer id"
            )
        return customer_id

    def create_account(
        self,
        enterprise_id: int,
        enterprise_name: str,
        billing_email: str,
        plan_id: int,
        count: int,
        customer_id: Optional[str] = None,
    ) -> object:
        """
        Creates a new billing account.

        Args:
            enterprise_id (int): The ID of the enterprise.
            enterprise_name (str): The name of the enterprise.
            billing_email (str): The billing email address.
            plan_id (int): The plan ID.
            count (int): Subscription count.
            customer_id (Optional[str]): Customer ID (optional).
        Returns:
            object: The created billing account object.
        """
        return self.create_object(
            id=str(enterprise_id),
            name=enterprise_name,
            planId=str(plan_id),
            subscriptionCount=count,
            customer=customer_id,
            billingEmail=billing_email,
        )

    def create_setup_intent(
        self,
        enterprise_id: int,
        payment_method_types: Optional[list[str]] = None,
        correlation_id: Optional[str] = None,
    ) -> object:
        """Create a Stripe SetupIntent for the billing account's customer."""

        customer_id = self._get_customer_id_for_enterprise(enterprise_id)
        payload: dict[str, Any] = {
            "customer_id": customer_id,
            "account_id": str(enterprise_id),
        }
        if payment_method_types is not None:
            payload["payment_method_types"] = payment_method_types
        if correlation_id is not None:
            payload["correlation_id"] = correlation_id

        return self._billing_request("post", self._setup_intents_url(), payload)

    def get_setup_intent(
        self,
        intent_id: str,
        enterprise_id: Optional[int] = None,
        correlation_id: Optional[str] = None,
    ) -> object:
        """Retrieve a Stripe SetupIntent without exposing bridge routing details to callers."""

        params: dict[str, Any] = {}
        if enterprise_id is not None:
            params["account_id"] = str(enterprise_id)
        if correlation_id is not None:
            params["correlation_id"] = correlation_id

        return self._billing_request(
            "get",
            self._setup_intents_url(intent_id),
            params or None,
        )

    def get_account_state(
        self,
        enterprise_id: int,
        correlation_id: Optional[str] = None,
    ) -> object:
        """Retrieve the Stripe-derived account state for a billing account."""

        customer_id = self._get_customer_id_for_enterprise(enterprise_id)
        params: dict[str, Any] = {"account_id": str(enterprise_id)}
        if correlation_id is not None:
            params["correlation_id"] = correlation_id

        return self._billing_request(
            "get",
            self._account_state_url(customer_id),
            params,
        )

    def delete_account(self, enterprise_id: int) -> None:
        """
        Deletes a billing account by enterprise ID.

        Args:
            enterprise_id (int): The ID of the enterprise.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(enterprise_id))
            requestor.request("delete", url)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to delete account for enterprise_id={enterprise_id}: {exc}"
            ) from exc

    def update_account(
        self,
        enterprise_id: int,
        name: Optional[str] = None,
        plan_id: Optional[int] = None,
        subscription_count: Optional[int] = None,
        plan_change_strategy: Optional[str] = None,
        billing_email: Optional[str] = None,
    ) -> object:
        """
        Updates a billing account.

        Args:
            enterprise_id (int): The ID of the enterprise.
            name (Optional[str]): New name (optional).
            plan_id (Optional[int]): New plan ID (optional).
            subscription_count (Optional[int]): New subscription count (optional).
            plan_change_strategy (Optional[str]): Plan change strategy (optional).
            billing_email (Optional[str]): New billing email (optional).
        Returns:
            object: The updated billing account object.
        """
        params: dict[str, object] = {"id": str(enterprise_id)}
        if name is not None:
            params["name"] = name
        if plan_id is not None:
            params["planId"] = str(plan_id)
        if subscription_count is not None:
            params["subscriptionCount"] = subscription_count
        if billing_email is not None:
            params["billingEmail"] = billing_email
        if plan_change_strategy is not None:
            params["planChangeStrategy"] = plan_change_strategy
        return self.update_object(obj_id=enterprise_id, **params)

    def change_plan(
        self,
        enterprise_id: int,
        plan_id: int,
        plan_change_strategy: Optional[str] = None,
    ) -> object:
        """
        Changes the plan for a billing account.

        Args:
            enterprise_id (int): The ID of the enterprise.
            plan_id (int): The new plan ID.
            plan_change_strategy (Optional[str]): Plan change strategy (optional).
        Returns:
            object: The updated billing account object.
        """
        params: dict[str, object] = {}
        if plan_change_strategy is not None:
            params["planChangeStrategy"] = plan_change_strategy
        return self.update_object(
            obj_id=enterprise_id, id=str(enterprise_id), planId=str(plan_id), **params
        )

    def add_user(self, enterprise_id: int, count: int = 1) -> "BillingAccount":
        """
        Adds a user to the enterprise.

        Args:
            enterprise_id (int): The ID of the enterprise.
            count (int): Number of users to add (default: 1).
        Returns:
            BillingAccount: The updated BillingAccount instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(enterprise_id))}/users"
            response = requestor.request("post", url, {"subscriptionCount": count})
            self.refresh_from(response)
            return self
        except (ValueError, TypeError, RuntimeError) as exc:
            raise RuntimeError(
                f"Failed to add user(s) to enterprise_id={enterprise_id}: {exc}"
            ) from exc

    def delete_user(self, enterprise_id):
        """Deletes a user"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/users"
        requestor.request("delete", url)

    def get_payment_data(self, enterprise_id):
        """To get the payment data for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/subscription"
        response = requestor.request("get", url)
        self.refresh_from(response)

        return self

    def adjust_balance(
        self,
        enterprise_id,
        balance_adjustment,
        adjustment_type,
        description,
        prorate=False,
        void=False,
    ):
        """Adjusts the balance for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/balance"
        response = requestor.request(
            "put",
            url,
            {
                "balanceAdjustment": balance_adjustment,
                "adjustmentType": adjustment_type,
                "description": description,
                "prorate": prorate,
                "void": void,
            },
        )
        self.refresh_from(response)

        return response

    def get_plan_data(self, enterprise_id):
        """To get the plan data"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/plan"
        response = requestor.request("get", url)
        self.refresh_from(response)

        return self

    def get_plan_history(self, enterprise_id, offset, limit):
        """To get the plan history"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/plan_history"
        response = requestor.request("get", url, {"offset": offset, "limit": limit})
        self.refresh_from(response)

        return self

    def get_invoice(self, enterprise_id, invoice_id):
        """To get the invoice"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/invoices/{invoice_id}"
        response = requestor.request("get", url)
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
        response = requestor.request("post", url, data)
        self.refresh_from(response)

        return self

    def get_charge(self, enterprise_id, charge_id):
        """To get the change"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/charges/{charge_id}"
        response = requestor.request("get", url)
        self.refresh_from(response)

        return self

    def update_email(self, enterprise_id, billing_email):
        """To update an email"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/update_email"
        response = requestor.request("put", url, {"email": billing_email})
        self.refresh_from(response)

        return response

    @classmethod
    def class_url(cls):
        """Returns a URL for the account"""
        return "/api/v2/accounts"
