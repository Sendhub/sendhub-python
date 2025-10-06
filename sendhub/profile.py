from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import PROFILE_BASE


class Profile(APIResource):
    """Class for Profile"""
    @staticmethod
    def get_base_url():
        """Returns the base URL for Profile"""
        return PROFILE_BASE

    def fetch(self, user_id):
        """Get the profile for the given user"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id))
        response = requestor.request('get', url)
        self.refresh_from(response)
        return self

    def update(self, user_id, data):
        """Updates the user by user_id"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id))
        requestor.request('patch', url, data)
        return self

    def get_user(self, user_id):
        """To get the user by user_id"""
        return self.get_object(user_id)

    @classmethod
    def class_url(cls):
        """Returns a URL for Profile"""
        return f"/api/v3/{cls.class_name()}s"
