import urllib

from sendhub.api_requestor import APIRequestor
from sendhub.constants import API_BASE
from sendhub.sendhub_error import InvalidRequestError
from sendhub.sendhub_object import SendHubObject


class APIResource(SendHubObject):
    """class for APIResource"""
    @staticmethod
    def get_base_url():
        """Returns the base URL for API Resource"""
        return API_BASE

    def get_object(self, obj_id):
        """To get an object"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        response = requestor.request(meth='get', url=url)
        self.refresh_from(response)
        self._id = obj_id
        return self

    def get_list(self, **params):
        """To get the list"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        response = requestor.request(meth='get', url=self.class_url(), params=params)
        return [SendHubObject.construct_from(i) for i in response]

    def create_object(self, **params):
        """Creates an object for APIResource"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.class_url()
        response = requestor.request(meth='post', url=url, params=params)
        self.refresh_from(response)

        return self

    def update_object(self, obj_id, **params):
        """Updates an object"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        response = requestor.request(meth='put', url=url, params=params)
        self.refresh_from(response)
        self._id = obj_id

        return self

    def instance_url(self, _id=None):
        """To get the instance url"""
        _id = self.get('id') if _id is None else _id
        if not _id:
            raise InvalidRequestError(f"Could not determine which URL to request: {type(self).__name__} instance has invalid ID: {_id}", 'id')
        _id = APIRequestor.utf8(_id)
        base = self.class_url()
        extn = urllib.parse.quote_plus(_id)
        return f"{base}/{extn}"

    @classmethod
    def class_name(cls):
        """Forms URL for the class for API Resource"""
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return f"{urllib.parse.quote_plus(cls.__name__.lower())}"

    @classmethod
    def class_url(cls):
        """Returns URL for the class for API Resource"""
        return f"/v1/{cls.class_name()}s"


