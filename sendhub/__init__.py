# -*- coding: utf-8 -*-
# pylint: disable=W0107, W0703, R0913, R0914, C0302
""" SendHub Python bindings """

import logging
import re
import platform
import sys
import urllib.parse
import textwrap
import datetime
import math as _math
import time as _time
import simplejson as json
import requests
from .version import VERSION

try:
    import io as StringIO
except ImportError:
    import io

HTTP_LIB = 'requests'
LOGGER = logging.getLogger('sendhub')

# Configuration variables
USERNAME = None
PASSWORD = None
INTERNAL_API = False
API_BASE = 'https://api.sendhub.com'
ENTITLEMENTS_BASE = 'https://entitlements.sendhub.com'
PROFILE_BASE = 'https://profile.sendhub.com'
BILLING_BASE = 'https://billing.sendhub.com'
API_VERSION = None


# Exceptions
class SendHubError(Exception):
    """Custom Exception for SendHub"""
    def __init__(
            self, message=None, dev_message=None, code=None, more_info=None):
        super().__init__(message)
        self.dev_message = dev_message \
            if dev_message is not None else ''
        self.code = code if code is not None else -1
        self.more_info = more_info \
            if more_info is not None else ''


_UNDERSCORER1 = re.compile(r'(.)([A-Z][a-z]+)')
__UNDERSCORER2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(_s):
    """
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    subbed = _UNDERSCORER1.sub(r'\1_\2', _s)
    return __UNDERSCORER2.sub(r'\1_\2', subbed).lower()


def retry(tries, delay=3, backoff=2, desired_outcome=True, _fail_value=None):
    """
    Retry decorator with exponential backoff
    Retries a function or method until it produces a desired outcome.

    @param tries: no of try
    @param delay int Sets the initial delay in seconds, and backoff sets the
        factor by which the delay should lengthen after each failure.
    @param backoff int Must be greater than 1, or else it isn't really a
        backoff.  Tries must be at least 0, and delay greater than 0.
    @param desired_outcome Can be a value or a callable.
        If it is a callable the produced value will be passed and success
        is presumed if the invocation returns True.
    @param _fail_value Value to return in the case of failure.
    """

    if backoff <= 1:
        raise ValueError('backoff must be greater than 1')

    tries = _math.floor(tries)
    if tries < 0:
        raise ValueError('tries must be 0 or greater')

    if delay <= 0:
        raise ValueError('delay must be greater than 0')

    def wrapped_retry(_fn):
        """Decorative wrapper."""

        def retry_fn(*args, **kwargs):
            """The function which does the actual retrying."""
            # Make mutable:
            mtries, mdelay = tries, delay

            # First attempt.
            _rv = _fn(*args, **kwargs)

            while mtries > 0:
                if (_rv == desired_outcome or (callable(desired_outcome) and
                                               desired_outcome(_rv) is True)):
                    # Success.
                    return _rv

                # Consume an attempt.
                mtries -= 1

                # Wait...
                _time.sleep(mdelay)

                # Make future wait longer.
                mdelay *= backoff

                # Try again.
                _rv = _fn(*args, **kwargs)

            # Ran out of tries :-(
            return False

        # True decorator -> decorated function.
        return retry_fn

    # @retry(arg[, ...]) -> decorator.
    return wrapped_retry


class APIError(SendHubError):
    """Exception class for API Error"""
    pass


class APIConnectionError(SendHubError):
    """Exception class for API Connection Error"""
    pass


class EntitlementError(SendHubError):
    """Exception class for Entitlement Error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class InvalidRequestError(SendHubError):
    """Exception class for Invalid Request Error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class TryAgainLaterError(SendHubError):
    """Exception class for Try AgainLater error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class AuthenticationError(SendHubError):
    """Exception class for Authentication Error"""
    pass


class AuthorizationError(SendHubError):
    """Exception class for Authorization Error"""
    pass


def convert_to_sendhub_object(resp):
    """Converts response object to send hub object"""
    types = {'entitlement': Entitlement}

    if isinstance(resp, list):
        return [convert_to_sendhub_object(i) for i in resp]
    if isinstance(resp, dict):
        resp = resp.copy()
        klass_name = resp.get('object')
        if isinstance(klass_name, str):
            klass = types.get(klass_name, SendHubObject)
        else:
            klass = SendHubObject
        return klass.construct_from(resp)
    return resp


class APIRequestor:
    """Network Transport class"""
    api_base = None

    def api_url(self, url=''):
        """Makes url with base url"""
        return '%s%s/' % \
               (self.api_base if self.api_base is not None else API_BASE, url)

    @classmethod
    def utf8(cls, value):
        """class method to convert value utf-8 encode"""
        if isinstance(value, str) and sys.version_info < (3, 0):
            return value.encode('utf-8')
        return value

    @classmethod
    def encode_datetime(cls, dttime):
        """Formats datetime"""
        return dttime.strftime('%Y-%m-%dT%H:%M:%S')

    @classmethod
    def encode_list(cls, listvalue):
        """only supports lists of things that can be represented as strings"""
        return ','.join(map(str, listvalue))

    @classmethod
    def _encode_inner(cls, _d):
        """special case value encoding"""
        encoders = {
            list: cls.encode_list,
            datetime.datetime: cls.encode_datetime
        }

        stk = {}
        for key, value in list(_d.items()):
            key = cls.utf8(key)
            try:
                encoder = encoders[value.__class__]
                stk[key] = encoder(value)
            except KeyError:
                # don't need special encoding
                value = cls.utf8(value)
                stk[key] = value
        return stk

    @classmethod
    def encode(cls, _d):
        """
        Internal: encode a string for url representation
        """
        return urllib.parse.urlencode(cls._encode_inner(_d))

    @classmethod
    def encode_json(cls, _d):
        """
        Internal: encode a string for url representation
        """
        return json.dumps(cls._encode_inner(_d))

    @classmethod
    def build_url(cls, url, params, auth_params_only=False):
        """Class method to build url"""
        if auth_params_only:

            new_params = {}

            for param in params:
                if param in ('username', 'password',
                             'apiUsername', 'apiPassword'):
                    new_params[param] = params[param]
            params = new_params
        base_query = urllib.parse.urlparse(url).query
        if base_query:
            return '%s&%s' % (url, cls.encode(params))
        return '%s?%s' % (url, cls.encode(params))

    def request(self, meth, url, params=None):
        """Handles requests"""
        resp = []
        params = params if params else {}

        @retry(tries=3)
        def _wrapped_request():
            rbody, rcode = self.perform_request(meth, url, params)
            try:
                resp.append(self.interpret_response(rbody, rcode))
            except TryAgainLaterError:
                return False
            return True

        if _wrapped_request():
            return resp[0]
        raise APIError('API retries failed')

    @staticmethod
    def handle_api_error(rbody, rcode, resp):
        """Handles API Error"""
        try:
            # message is required
            message = resp['message']
        except (KeyError, TypeError) as err:
            raise APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode), '', rcode, '') from err

        if 'dev_message' in resp:
            dev_message = resp['dev_message']
        else:
            dev_message = ''

        if 'code' in resp:
            code = resp['code']
        else:
            code = -1

        if 'more_info' in resp:
            more_info = resp['more_info']
        else:
            more_info = ''

        if rcode in [400, 404]:
            raise InvalidRequestError(message, dev_message, code, more_info)
        if rcode == 401:
            raise AuthenticationError(message, dev_message, code, more_info)
        if rcode == 403:
            raise AuthorizationError(message, dev_message, code, more_info)
        if rcode == 409 and 'Try again later' in message:
            raise TryAgainLaterError(message, dev_message, code, more_info)
        raise APIError(message, dev_message, code, more_info)

    def perform_request(self, meth, url, params=None):
        """
        Mechanism for issuing an API call
        """
        if USERNAME is None or PASSWORD is None:
            raise AuthenticationError('No authentication details provided')

        abs_url = self.api_url(url)
        params = params.copy() if params else {}
        if INTERNAL_API:
            params['apiUsername'] = USERNAME
            params['apiPassword'] = PASSWORD
        else:
            params['username'] = USERNAME
            params['api_key'] = PASSWORD

        _ua = {
            'bindingsVersion': VERSION,
            'lang': 'python',
            'publisher': 'sendhub',
            'httplib': HTTP_LIB,
        }
        for attr, func in [['langVersion', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception as exp_err:
                val = "!! %s" % exp_err
            _ua[attr] = val

        headers = {
            'Content-Type': 'application/json',
            'X-SendHub-Client-User-Agent': json.dumps(_ua),
            'User-Agent': 'SendHub/v1 PythonBindings/%s' % (VERSION,)
        }
        if API_VERSION is not None:
            headers['SendHub-Version'] = API_VERSION

        rbody, rcode = self.do_send_request(meth, abs_url, headers, params)

        request_info = 'API request to %s returned (response code, ' \
                       'response body) of (%d, %r)', (abs_url, rcode, rbody)
        LOGGER.info(request_info)

        return rbody, rcode

    def interpret_response(self, rbody, rcode):
        """special case deleted because the response is empty"""
        if rcode == 204:
            resp = {
                'message': 'OK'
            }
            return resp

        try:
            resp = json.loads(rbody.decode('utf-8'))
        except Exception as exp:
            raise APIError(
                "Invalid response body from API: %s (HTTP response code "
                "was %d)" % (rbody, rcode), '', rcode) from exp
        if not 200 <= rcode < 300:
            self.handle_api_error(rbody, rcode, resp)
        return resp

    def do_send_request(self, meth, abs_url, headers, params):
        """Sends request"""
        content = ""
        status_code = ""
        meth = meth.lower()
        if meth in ('get', 'delete'):
            if params:
                abs_url = self.build_url(abs_url, params)
            data = None
        elif meth in ('post', 'put', 'patch'):
            abs_url = self.build_url(abs_url, params, True)

            new_params = {}
            for param in params:
                if param not in ('username', 'password',
                                 'apiUsername', 'apiPassword'):
                    new_params[param] = params[param]
            params = new_params

            data = self.encode_json(params)
        else:
            raise APIConnectionError(
                'Unrecognized HTTP method %r.  This may indicate a bug '
                'in the SendHub bindings.  Please contact support@sendhub.com '
                'for assistance.' % (meth,))

        kwargs = {}
        try:
            try:
                result = requests.request(meth, abs_url,
                                          headers=headers, data=data,
                                          timeout=80,
                                          **kwargs)
            except TypeError as typ_err:
                raise TypeError(
                    'Warning: It looks like your installed version of the '
                    '"requests" library is not compatible. The underlying '
                    'error was: %s' % (typ_err,)) from typ_err

            content = result.content
            status_code = result.status_code
        except Exception as exp_err:
            self.handle_request_error(exp_err)
        return content, status_code

    @staticmethod
    def handle_request_error(_e):
        """Handles a request error"""
        if isinstance(_e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with SendHub.  If this " \
                  "problem persists, let us know at support@sendhub.com."
            err = "%s: %s" % (type(_e).__name__, str(_e))
        else:
            msg = "Unexpected error communicating with SendHub.  It looks " \
                  "like there's probably a configuration issue locally.  " \
                  "If this problem persists, let us know at " \
                  "support@sendhub.com."
            err = "A %s was raised" % (type(_e).__name__,)
            if str(_e):
                err += " with error message %s" % (str(_e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: " + err + ")"
        raise APIConnectionError(msg)


class SendHubObject:
    """Class to make SendHub object"""
    def __init__(self, _id=None, **_params):
        self.__dict__['_values'] = set()
        self._id = ""

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        self._values.add(k)

    def __getattr__(self, k):
        try:
            return self.__dict__[k]
        except KeyError:
            pass

    def __getitem__(self, k):
        if k in self._values:
            return self.__dict__[k]
        raise KeyError(k)

    def get(self, k, default=None):
        """Get object value"""
        try:
            return self[k]
        except KeyError:
            return default

    def setdefault(self, k, default=None):
        """Sets the default value if key does not exist"""
        try:
            return self[k]
        except KeyError:
            self[k] = default
            return default

    def __setitem__(self, k, val):
        setattr(self, k, val)

    def keys(self):
        """Returns keys"""
        return list(self.to_dict().keys())

    def values(self):
        """Returns values"""
        return list(self.to_dict().values())

    @classmethod
    def construct_from(cls, values):
        """Class method for constructing the dict"""
        instance = cls(values.get('id'))
        instance.refresh_from(values)
        return instance

    def refresh_from(self, values):
        """refresh from dict"""
        for k, val in list(values.items()):
            name = camel_to_snake(k)
            self.__dict__[name] = convert_to_sendhub_object(val)
            self._values.add(name)

    def __repr__(self):
        """class string representation"""
        type_string = ''
        if isinstance(self.get('object'), str):
            type_string = ' %s' % self.get('object').encode('utf8')

        id_string = ''
        if isinstance(self.get('id'), str):
            id_string = ' id=%s' % self.get('id').encode('utf8')

        return '<%s%s%s at %s> JSON: %s' % (
            type(self).__name__, type_string, id_string, hex(id(self)),
            json.dumps(self.to_dict(), sort_keys=True, indent=2,
                       cls=SendHubObjectEncoder)
        )

    def __str__(self):
        """string representation for an object"""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2,
                          cls=SendHubObjectEncoder)

    def to_dict(self):
        """Converts obj as dict"""
        def _serialize(_o):
            if isinstance(_o, SendHubObject):
                return _o.to_dict()
            if isinstance(_o, list):
                return [_serialize(i) for i in _o]
            return _o

        _d = dict()
        for k in sorted(self._values):
            _v = getattr(self, k)
            _v = _serialize(_v)
            _d[k] = _v
        return _d


class SendHubObjectEncoder(json.JSONEncoder):
    """Class for SendHub object encoder"""
    # pylint: disable=method-hidden, arguments-differ
    def default(self, obj):
        """Converts obj to dict"""
        if isinstance(obj, SendHubObject):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


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
        response = requestor.request('get', url)
        self.refresh_from(response)
        self._id = obj_id
        return self

    def get_list(self, **params):
        """To get the list"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        response = requestor.request(
            meth='get', url=self.class_url(), params=params)
        return [SendHubObject.construct_from(i) for i in response]

    def create_object(self, **params):
        """Creates an object for APIResource"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.class_url()
        response = requestor.request('post', url, params)
        self.refresh_from(response)

        return self

    def update_object(self, obj_id, **params):
        """Updates an object"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        response = requestor.request('put', url, params)
        self.refresh_from(response)
        self._id = obj_id

        return self

    @classmethod
    def class_name(cls):
        """Forms URL for the class for API Resource"""
        if cls == APIResource:
            raise NotImplementedError('APIResource is an abstract class.')
        return "%s" % urllib.parse.quote_plus(cls.__name__.lower())

    @classmethod
    def class_url(cls):
        """Returns URL for the class for API Resource"""
        clsname = cls.class_name()
        return "/v1/%ss" % clsname

    def instance_url(self, _id=None):
        """To get the instance url"""
        _id = self.get('id') if _id is None else _id
        if not _id:
            raise InvalidRequestError(
                'Could not determine which URL to request: %s instance has '
                'invalid ID: %r' % (type(self).__name__, _id), 'id')
        _id = APIRequestor.utf8(_id)
        base = self.class_url()
        extn = urllib.parse.quote_plus(_id)
        return "%s/%s" % (base, extn)


# API objects
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
            raise EntitlementError(str(aut_err), aut_err.dev_message,
                                   aut_err.code, aut_err.more_info) \
                from aut_err

        return self

    def confirm_update(self):
        """Updates the confirm"""
        if self._id is None:
            raise InvalidRequestError('An id(uuid) must be set prior '
                                      'to confirming')

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
        url = '{}/limits'.format(self.instance_url(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refresh_from(response)
        return self

    def check(self, enterprise_id, user_id, action, **params):
        """get the user of enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/{}/{}'.format(
            self.instance_url(str(enterprise_id)), str(user_id), str(action))
        response = requestor.request('get', url, params)
        self.refresh_from(response)

        return self

    def update(self, enterprise_id, user_id, action, **params):
        """To update the user of enterprise"""
        try:
            requestor = APIRequestor()
            requestor.api_base = self.get_base_url()
            url = '{}/{}/{}'.format(
                self.instance_url(str(enterprise_id)),
                str(user_id),
                str(action))
            response = requestor.request('post', url, params)
            self.refresh_from(response)
        except AuthorizationError as aut_err:
            raise EntitlementError(str(aut_err), aut_err.dev_message,
                                   aut_err.code, aut_err.more_info) \
                from aut_err

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
            url = '{}/limits/{}/{}'.format(
                self.instance_url(str(enterprise_id)),
                str(limit),
                str(value))
            response = requestor.request('post', url, params)
            self.refresh_from(response)

        except AuthorizationError as aut_err:
            raise EntitlementError(str(aut_err), aut_err.dev_message,
                                   aut_err.code, aut_err.more_info) \
                from aut_err

        return self

    @classmethod
    def class_url(cls):
        """Returns the URL for class of EntitlementV2"""
        return "/api/v2/entitlements"


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
        clsname = cls.class_name()
        return "/api/v3/%ss" % clsname


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
        clsname = cls.class_name()
        return "/api/v3/%ss" % clsname


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

        return self.update_object(
            obj_id=enterprise_id,
            id=str(enterprise_id),
            planId=str(plan_id),
            **params)

    def add_user(self, enterprise_id, count=1):
        """Add a user to the enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/users'.format(self.instance_url(str(enterprise_id)))
        response = requestor.request('post', url, {'subscriptionCount': count})
        self.refresh_from(response)

        return self

    def delete_user(self, enterprise_id):
        """Deletes a user"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/users'.format(self.instance_url(str(enterprise_id)))
        requestor.request('delete', url)

    def get_payment_data(self, enterprise_id):
        """To get the payment data for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/subscription'.format(
            self.instance_url(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def adjust_balance(
            self,
            enterprise_id,
            balance_adjustment,
            adjustment_type,
            description,
            prorate=False
    ):
        """Adjusts the balance for the given enterprise"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/balance'.format(
            self.instance_url(str(enterprise_id))
        )
        response = requestor.request(
            'put',
            url,
            {
                'balanceAdjustment': balance_adjustment,
                'adjustmentType': adjustment_type,
                'description': description,
                'prorate': prorate
            }
        )
        self.refresh_from(response)

        return response

    def get_plan_data(self, enterprise_id):
        """To get the plan data"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/plan'.format(
            self.instance_url(str(enterprise_id)))
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def get_plan_history(self, enterprise_id, offset, limit):
        """To get the plan history"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/plan_history'.format(
            self.instance_url(str(enterprise_id)))
        response = requestor.request(
            'get', url, {'offset': offset, 'limit': limit})
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

    def get_charge(self, enterprise_id, charge_id):
        """To get the change"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/charges/{}'.format(
            self.instance_url(str(enterprise_id)), charge_id)
        response = requestor.request('get', url)
        self.refresh_from(response)

        return self

    def update_email(self, enterprise_id, billing_email):
        """To update an email"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = '{}/update_email'.format(
            self.instance_url(str(enterprise_id))
        )
        response = requestor.request(
            'put',
            url,
            {
                'email': billing_email
            }
        )
        self.refresh_from(response)

        return response

    @classmethod
    def class_url(cls):
        """Returns a URL for the account"""
        return "/api/v2/accounts"


class BillingPlans(APIResource):
    """Class representing Billing Plans"""
    @staticmethod
    def get_base_url():
        """To get the base url for the BillingPlans API"""
        return BILLING_BASE

    def list_plans(self, with_hidden=True, active_status='all'):
        """To list the plans"""
        return self.get_list(
            with_hidden='1' if with_hidden else '0',
            active_status=active_status)

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
            maxVoiceMinutes=str(max_voice_minutes),
            maxConferenceLines=str(max_conference_lines),
            maxConferenceParticipants=str(max_conference_participants),
            marketingLines=marketing_lines,
            autoAttendant=auto_attendant,
            maxApiRequests=str(max_api_requests),
            maxBasicVmTranscriptions=str(max_basic_vm_transcriptions),
            maxPremiumVmTranscriptions=str(max_premium_vm_transcriptions),
            dataExport=data_export)

    def update_plan(self, plan_id, active):
        """To update the plan"""
        return self.update_object(
            obj_id=plan_id,
            id=plan_id,
            active=active)

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


class CreditCardBlacklist(APIResource):
    """class for CreditCardBlacklist"""
    @staticmethod
    def get_base_url():
        """To get the base URL"""
        return BILLING_BASE

    def list_blacklist(self, search_query=None):
        """Lists the blacklist items"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()

        search_url = [self.class_url()]

        if search_query:
            search_url.append('/{}'.format(search_query))

        url = ''.join(search_url)

        response = requestor.request(
            meth='get', url=url, params={})
        return [SendHubObject.construct_from(i) for i in response]

    def get_blacklist_item(self, item_id):
        """To get the blacklist item"""
        return self.get_object(item_id)

    def create_blacklist_item(
            self,
            fingerprint):
        """Creates a blacklist item"""
        return self.create_object(
            fingerprint=fingerprint)

    def delete_blacklist_item(self, item_id):
        """Deleted the blacklist item."""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(item_id))
        requestor.request('delete', url)

    @classmethod
    def class_url(cls):
        """Returns url for the class"""
        return "/api/v2/cards/blacklist"
