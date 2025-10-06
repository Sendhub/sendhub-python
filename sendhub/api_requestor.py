

import datetime
import json
import platform
import sys
import textwrap
import urllib

import requests

from sendhub.constants import API_BASE, API_VERSION, HTTP_LIB, INTERNAL_API, LOGGER, PASSWORD, USERNAME
from sendhub.sendhub_error import APIConnectionError, APIError, AuthenticationError, AuthorizationError, InvalidRequestError, TryAgainLaterError
from sendhub.utils import retry
from sendhub.version import VERSION


class APIRequestor:
    """Network Transport class"""
    api_base = None

    def api_url(self, url=''):
        """Makes url with base url"""
        return '%s%s/' % (self.api_base if self.api_base is not None else API_BASE, url)

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
        params = params if params else {"apiUsername": USERNAME, "apiPassword": PASSWORD}

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

        LOGGER.info(f'API request to {abs_url} returned response code: {rcode} & response body: {rbody}')

        return rbody, rcode

    def interpret_response(self, rbody, rcode):
        """special case deleted because the response is empty"""
        if rcode == 204:
            resp = { 'message': 'OK' }
            return resp

        try:
            if isinstance(rbody, bytes):
                resp = json.loads(rbody.decode('utf-8'))
            else:
                resp = json.loads(rbody)
        except Exception as exp:
            raise APIError(message = f"Invalid response body from API: {rbody} (HTTP response code was {rcode!r})", dev_message= '', code = rcode) from exp
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
                if param not in ('username', 'password', 'apiUsername', 'apiPassword'):
                    new_params[param] = params[param]
            params = new_params

            data = self.encode_json(params)
        else:
            raise APIConnectionError(f"Unrecognized HTTP method {meth}. This may indicate a bug in the SendHub bindings. Please contact support@sendhub.com for assistance.")

        kwargs = {}
        try:
            try:
                result = requests.request(meth, abs_url, headers=headers, data=data, timeout=80, **kwargs)
            except TypeError as typ_err:
                raise TypeError(f"Warning: It looks like your installed version of the `requests` library is not compatible. The underlying error was: {typ_err}") from typ_err

            content = result.content
            status_code = result.status_code
        except Exception as exp_err:
            self.handle_request_error(exp_err)
        return content, status_code

    @staticmethod
    def handle_request_error(_e):
        """Handles a request error"""
        if isinstance(_e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with SendHub. If this problem persists, let us know at support@sendhub.com."
            err = "%s: %s" % (type(_e).__name__, str(_e))
        else:
            msg = "Unexpected error communicating with SendHub. It looks like there's probably a configuration issue locally. If this problem persists, let us know at support@sendhub.com."
            err = "A %s was raised" % (type(_e).__name__,)
            if str(_e):
                err += " with error message %s" % (str(_e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: " + err + ")"
        raise APIConnectionError(msg)
