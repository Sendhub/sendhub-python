from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import ENTITLEMENTS_BASE
from sendhub.sendhub_error import (
    AuthorizationError,
    EntitlementError,
    InvalidRequestError,
)


class Entitlement(APIResource):
    """
    Class for Entitlement resource.
    Provides methods to check, update, confirm, and reset entitlements for users.
    """

    @classmethod
    def class_url(cls) -> str:
        """
        Returns the URL for the Entitlement class resource (v3 API).
        """
        return f"/api/v3/{cls.class_name()}s"

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base URL of Entitlement.
        """
        return ENTITLEMENTS_BASE

    def list_usage(self, user_id: int) -> "Entitlement":
        """
        List usages for a user.

        Args:
            user_id (int): The user ID.
        Returns:
            Entitlement: The updated Entitlement instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(user_id))
            response = requestor.request("get", url)
            self.refresh_from(response)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to list usage for user_id={user_id}: {exc}"
            ) from exc

    def check(self, user_id: int, action: str, **params: Any) -> "Entitlement":
        """
        Get the actions of a user.

        Args:
            user_id (int): The user ID.
            action (str): The action to check.
            params (Any): Additional parameters.
        Returns:
            Entitlement: The updated Entitlement instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(user_id))}/{action}"
            response = requestor.request("get", url, params)
            self.refresh_from(response)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to check entitlement for user_id={user_id}, action={action}: {exc}"
            ) from exc

    def update(self, user_id: int, action: str, **params: Any) -> "Entitlement":
        """
        Updates the user's action.

        Args:
            user_id (int): The user ID.
            action (str): The action to update.
            params (Any): Additional parameters.
        Returns:
            Entitlement: The updated Entitlement instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(user_id))}/{action}"
            response = requestor.request("post", url, params)
            self.refresh_from(response)
            self._id = self.uuid
            return self
        except AuthorizationError as aut_err:
            raise EntitlementError(
                str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info
            ) from aut_err
        except Exception as exc:
            raise RuntimeError(
                f"Failed to update entitlement for user_id={user_id}, action={action}: {exc}"
            ) from exc

    def confirm_update(self) -> "Entitlement":
        """
        Confirms the update for the entitlement.

        Returns:
            Entitlement: The updated Entitlement instance.
        Raises:
            InvalidRequestError: If _id (uuid) is not set.
            RuntimeError: If the update fails (e.g., due to missing authentication).
        """
        if getattr(self, "_id", None) is None:
            raise InvalidRequestError("An Id (uuid) must be set prior to confirming")
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = "/".join(
                [self.instance_url(str(self.user_id)), str(self.action), str(self._id)]
            )
            response = requestor.request("post", url)
            self.refresh_from(response)
            self._id = self.uuid
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to confirm update for entitlement: {exc}"
            ) from exc

    def reset(self, user_id: int, action: str, **_params: Any) -> "Entitlement":
        """
        Deletes the action of a user.

        Args:
            user_id (int): The user ID.
            action (str): The action to delete.
        Returns:
            Entitlement: The updated Entitlement instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(user_id))}/{action}"
            response = requestor.request("delete", url)
            self.refresh_from(response)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to reset entitlement for user_id={user_id}, action={action}: {exc}"
            ) from exc

    def reset_all(self, user_id: int, **_params: Any) -> "Entitlement":
        """
        Deletes all entitlements for a user by user_id.

        Args:
            user_id (int): The user ID.
        Returns:
            Entitlement: The updated Entitlement instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(user_id))
            response = requestor.request("delete", url)
            self.refresh_from(response)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to reset all entitlements for user_id={user_id}: {exc}"
            ) from exc


class EntitlementV2(APIResource):
    """
    Class for EntitlementV2 resource.
    Provides methods to list usage for enterprises.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base url of entitlements.
        """
        return ENTITLEMENTS_BASE

    def list_usage(self, enterprise_id: int) -> "EntitlementV2":
        """
        Lists the usage of the enterprise.

        Args:
            enterprise_id (int): The enterprise ID.
        Returns:
            EntitlementV2: The updated EntitlementV2 instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(enterprise_id))
            response = requestor.request("get", url)
            self.refresh_from(response)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to list usage for enterprise_id={enterprise_id}: {exc}"
            ) from exc
        return self

    def list_limits(self, enterprise_id):
        """lists the limits for the specified enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/limits"
        response = requestor.request("get", url)
        self.refresh_from(response)
        return self

    def check(self, enterprise_id, user_id, action, **params):
        """get the user of enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/{user_id}/{action}"
        response = requestor.request("get", url, params)
        self.refresh_from(response)

        return self

    def update(self, enterprise_id, user_id, action, **params):
        """To update the user of enterprise"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(enterprise_id))}/{user_id}/{action}"
            response = requestor.request("post", url, params)
            self.refresh_from(response)
        except AuthorizationError as aut_err:
            raise EntitlementError(
                str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info
            ) from aut_err

        return self

    def reset(self, enterprise_id, **_params):
        """Delete an enterprise by id"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(enterprise_id))
        response = requestor.request("delete", url)
        self.refresh_from(response)

        return self

    def update_limit(self, enterprise_id, limit, value, **params):
        """Updates the limit"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(enterprise_id))}/limits/{limit}/{value}"
            response = requestor.request("post", url, params)
            self.refresh_from(response)

        except AuthorizationError as aut_err:
            raise EntitlementError(
                str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info
            ) from aut_err

        return self

    @classmethod
    def class_url(cls):
        """Returns the URL for class of EntitlementV2"""
        return "/api/v2/entitlements"
