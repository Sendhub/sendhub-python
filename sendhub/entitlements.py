from sendhub.api_requestor import APIRequestor
from sendhub.api_resource import APIResource
from sendhub.constants import ENTITLEMENTS_BASE
from sendhub.sendhub_error import AuthorizationError, EntitlementError, InvalidRequestError


class Entitlement(APIResource):
    """Class of an Entitlement"""
    @staticmethod
    def get_base_url():
        """To get the base URL of Entitlement"""
        return ENTITLEMENTS_BASE

    def list_usage(self, user_id):
        """List usages"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id))
        response = requestor.request('get', url)
        self.refresh_from(response)
        return self

    def check(self, user_id, action, **params):
        """To get the actions of user_id"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id)) + '/' + str(action)
        response = requestor.request('get', url, params)
        self.refresh_from(response)

        return self

    def update(self, user_id, action, **params):
        """Updates the user's action"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = self.instance_url(str(user_id)) + '/' + str(action)
            response = requestor.request('post', url, params)
            self.refresh_from(response)
            self._id = self.uuid
        except AuthorizationError as aut_err:
            raise EntitlementError(str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info) from aut_err

        return self

    def confirm_update(self):
        """Updates the confirm"""
        if self._id is None:
            raise InvalidRequestError('An Id (uuid) must be set prior to confirming')

        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '/'.join([
            self.instance_url(str(self.user_id)),
            str(self.action),
            str(self._id)
        ])
        response = requestor.request('post', url)
        self.refresh_from(response)

        self._id = self.uuid

        return self

    def reset(self, user_id, action, **_params):
        """Delete the action of user"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id)) + '/' + str(action)
        response = requestor.request('delete', url)
        self.refresh_from(response)

        return self

    def reset_all(self, user_id, **_params):
        """Deletes the user by user_id"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(user_id))
        response = requestor.request('delete', url)
        self.refresh_from(response)

        return self


class EntitlementV2(APIResource):
    """Class of EntitlementV2"""
    @staticmethod
    def get_base_url():
        """To get the base url of entitlements"""
        return ENTITLEMENTS_BASE

    def list_usage(self, enterprise_id):
        """Lists the usage of the enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(enterprise_id))
        response = requestor.request('get', url)
        self.refresh_from(response)
        return self

    def list_limits(self, enterprise_id):
        """lists the limits for the specified enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/limits"
        response = requestor.request('get', url)
        self.refresh_from(response)
        return self

    def check(self, enterprise_id, user_id, action, **params):
        """get the user of enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = f"{self.instance_url(str(enterprise_id))}/{user_id}/{action}"
        response = requestor.request('get', url, params)
        self.refresh_from(response)

        return self

    def update(self, enterprise_id, user_id, action, **params):
        """To update the user of enterprise"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(enterprise_id))}/{user_id}/{action}"
            response = requestor.request('post', url, params)
            self.refresh_from(response)
        except AuthorizationError as aut_err:
            raise EntitlementError(str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info) from aut_err

        return self

    def reset(self, enterprise_id, **_params):
        """Delete an enterprise by id"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(enterprise_id))
        response = requestor.request('delete', url)
        self.refresh_from(response)

        return self

    def update_limit(self, enterprise_id, limit, value, **params):
        """Updates the limit"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = f"{self.instance_url(str(enterprise_id))}/limits/{limit}/{value}"
            response = requestor.request('post', url, params)
            self.refresh_from(response)

        except AuthorizationError as aut_err:
            raise EntitlementError(str(aut_err), aut_err.dev_message, aut_err.code, aut_err.more_info) from aut_err

        return self

    @classmethod
    def class_url(cls):
        """Returns the URL for class of EntitlementV2"""
        return "/api/v2/entitlements"
