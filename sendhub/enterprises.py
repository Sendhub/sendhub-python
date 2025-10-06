from sendhub.api_resource import APIResource
from sendhub.constants import PROFILE_BASE


class Enterprise(APIResource):
    """Class for enterprise"""
    @staticmethod
    def get_base_url():
        """To get the base URL for enterprise"""
        return PROFILE_BASE

    def get_enterprise(self, enterprise_id):
        """To get the enterprise"""
        return self.get_object(enterprise_id)

    @classmethod
    def class_url(cls):
        """Returns the URL for the class"""
        return f"/api/v3/{cls.class_name()}s"
