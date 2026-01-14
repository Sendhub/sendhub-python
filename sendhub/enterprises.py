from typing import Any

from sendhub.api_resource import APIResource
from sendhub.constants import PROFILE_BASE


class Enterprise(APIResource):
    """
    Class for Enterprise resource.
    Provides methods to retrieve enterprise information.
    """

    @staticmethod
    def get_base_url() -> str:
        """
        Returns the base URL for enterprise.
        """
        return PROFILE_BASE

    def get_enterprise(self, enterprise_id: int) -> Any:
        """
        Retrieves the enterprise by ID.

        Args:
            enterprise_id (int): The enterprise ID.
        Returns:
            Any: The enterprise object.
        Raises:
            ValueError: If enterprise_id is None.
        """
        if enterprise_id is None:
            raise ValueError("enterprise_id must not be None")
        return self.get_object(enterprise_id)

    @classmethod
    def class_url(cls) -> str:
        """
        Returns the URL for the Enterprise class resource.
        """
        return f"/api/v3/{cls.class_name()}s"
