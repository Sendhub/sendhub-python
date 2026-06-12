from typing import Any

from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import PROFILE_BASE


class Profile(APIResource):
    """
    Class for Profile resource.
    Provides methods to fetch, update, and retrieve user profiles.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base URL for Profile.
        """
        return PROFILE_BASE

    def fetch(self, user_id: int) -> "Profile":
        """
        Get the profile for the given user.

        Args:
            user_id (int): The user ID.
        Returns:
            Profile: The updated Profile instance.
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
                f"Failed to fetch profile for user_id={user_id}: {exc}"
            ) from exc

    def update(self, user_id: int, data: dict[str, Any]) -> "Profile":
        """
        Updates the user by user_id.

        Args:
            user_id (int): The user ID.
            data (Dict[str, Any]): Data to update.
        Returns:
            Profile: The updated Profile instance.
        """
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(user_id))
            requestor.request("patch", url, data)
            return self
        except Exception as exc:
            raise RuntimeError(
                f"Failed to update profile for user_id={user_id}: {exc}"
            ) from exc

    def get_user(self, user_id: int) -> object:
        """
        Retrieves the user by user_id.

        Args:
            user_id (int): The user ID.
        Returns:
            object: The user object.
        """
        return self.get_object(user_id)

    @classmethod
    def class_url(cls) -> str:
        """
        Returns the URL for the Profile class resource.
        """
        return f"/api/v3/{cls.class_name()}s"
