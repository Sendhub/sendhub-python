import datetime
import json
import platform
import textwrap
import urllib.parse
from typing import Any, Dict, Optional

import requests

from sendhub.constants import (
    API_BASE,
    API_VERSION,
    HTTP_LIB,
    INTERNAL_API,
    LOGGER,
    PASSWORD,
    USERNAME,
)
from sendhub.sendhub_error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    AuthorizationError,
    InvalidRequestError,
    TryAgainLaterError,
)
from sendhub.utils import retry
from sendhub.version import VERSION


class APIRequestor:
    """
    Network Transport class for handling API requests.
    """

    api_base: Optional[str] = None

    def api_url(self, url: str = "") -> str:
        """
        Construct a full API URL using the base URL.

        Args:
            url (str): The endpoint path.
        Returns:
            str: The full API URL.
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url).__name__}")
        return f"{self.api_base if self.api_base is not None else API_BASE}{url}/"

    @classmethod
    def utf8(cls, value: Any) -> Any:
        """
        Convert value to UTF-8 encoding if needed (no-op for now).
        """
        return value

    @classmethod
    def encode_datetime(cls, dttime: datetime.datetime) -> str:
        """
        Format a datetime object as an ISO8601 string.
        """
        if not isinstance(dttime, datetime.datetime):
            raise TypeError("dttime must be a datetime object")
        return dttime.strftime("%Y-%m-%dT%H:%M:%S")

    @classmethod
    def encode_list(cls, listvalue: list[Any]) -> str:
        """
        Encode a list of values as a comma-separated string.
        """
        if not isinstance(listvalue, list):
            raise TypeError("listvalue must be a list")
        return ",".join(map(str, listvalue))

    @classmethod
    def _encode_inner(cls, _d: Dict[str, Any]) -> Dict[str, Any]:
        """
        Special case value encoding for lists and datetimes.
        """
        if not isinstance(_d, dict):
            raise TypeError("_d must be a dict")
        encoders = {
            list: cls.encode_list,
            datetime.datetime: cls.encode_datetime,
        }
        stk: Dict[str, Any] = {}
        for key, value in list(_d.items()):
            key = cls.utf8(key)
            try:
                encoder = encoders[value.__class__]
                stk[key] = encoder(value)
            except KeyError:
                value = cls.utf8(value)
                stk[key] = value
        return stk

    @classmethod
    def encode(cls, _d: Dict[str, Any]) -> str:
        """
        Encode a dictionary for URL representation.
        """
        return urllib.parse.urlencode(cls._encode_inner(_d))

    @classmethod
    def encode_json(cls, _d: Dict[str, Any]) -> str:
        """
        Encode a dictionary as a JSON string.
        """
        return json.dumps(cls._encode_inner(_d))

    @classmethod
    def build_url(
        cls, url: str, params: Dict[str, Any], auth_params_only: bool = False
    ) -> str:
        """
        Build a URL with query parameters.

        Args:
            url (str): The base URL.
            params (Dict[str, Any]): Query parameters.
            auth_params_only (bool): If True, only include auth params.
        Returns:
            str: The full URL with query string.
        """
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        if not isinstance(params, dict):
            raise TypeError("params must be a dict")
        if auth_params_only:
            new_params = {
                k: v
                for k, v in params.items()
                if k in ("username", "password", "apiUsername", "apiPassword")
            }
            params = new_params
        base_query = urllib.parse.urlparse(url).query
        if base_query:
            return f"{url}&{cls.encode(params)}"
        return f"{url}?{cls.encode(params)}"

    def request(self, meth: str, url: str, params: Optional[dict] = None) -> Any:
        """Handles requests"""
        if not isinstance(meth, str):
            raise TypeError("meth must be a string")
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        if params is not None and not isinstance(params, dict):
            raise TypeError("params must be a dict or None")

        resp = []
        params = (
            params if params else {"apiUsername": USERNAME, "apiPassword": PASSWORD}
        )

        # Credential validation
        if not USERNAME or not PASSWORD:
            LOGGER.error("Missing USERNAME or PASSWORD for SendHub API request.")
            raise AuthenticationError("No authentication details provided")

        LOGGER.debug(f"Preparing request: method={meth}, url={url}, params={params}")

        @retry(tries=3)
        def _wrapped_request():
            try:
                rbody, rcode = self.perform_request(meth, url, params)
                LOGGER.debug(f"Raw response: code={rcode}, body={rbody}")
                resp.append(self.interpret_response(rbody, rcode))
            except TryAgainLaterError as e:
                LOGGER.debug(f"TryAgainLaterError encountered: {e}")
                return False
            except Exception as e:
                LOGGER.debug(f"Exception during request: {e}")
                raise
            return True

        if _wrapped_request():
            LOGGER.debug(f"Request successful: {resp[0]}")
            return resp[0]
        LOGGER.error("API retries failed")
        raise APIError("API retries failed")

    @staticmethod
    def handle_api_error(rbody, rcode, resp):
        """Handles API Error"""
        try:
            # message is required
            message = resp["message"]
        except (KeyError, TypeError) as err:
            raise APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                "",
                rcode,
                "",
            ) from err

        dev_message = resp.get("dev_message", "")
        code = resp.get("code", -1)
        more_info = resp.get("more_info", "")

        if rcode in [400, 404]:
            raise InvalidRequestError(message, dev_message, code, more_info)
        if rcode == 401:
            raise AuthenticationError(message, dev_message, code, more_info)
        if rcode == 403:
            raise AuthorizationError(message, dev_message, code, more_info)
        if rcode == 409 and "Try again later" in message:
            raise TryAgainLaterError(message, dev_message, code, more_info)
        raise APIError(message, dev_message, code, more_info)

    def perform_request(self, meth, url, params=None):
        """
        Mechanism for issuing an API call
        """

        abs_url = self.api_url(url)
        params = params.copy() if params else {}
        if INTERNAL_API:
            params["apiUsername"] = USERNAME
            params["apiPassword"] = PASSWORD
        else:
            params["username"] = USERNAME
            params["api_key"] = PASSWORD

        _ua = {
            "bindingsVersion": VERSION,
            "lang": "python",
            "publisher": "sendhub",
            "httplib": HTTP_LIB,
        }
        for attr, func in [
            ["langVersion", platform.python_version],
            ["platform", platform.platform],
            ["uname", lambda: " ".join(platform.uname())],
        ]:
            try:
                val = func()
            except Exception as exp_err:
                val = f"!! {exp_err}"
            _ua[attr] = val

        headers = {
            "Content-Type": "application/json",
            "X-SendHub-Client-User-Agent": json.dumps(_ua),
            "User-Agent": f"SendHub/v1 PythonBindings/{VERSION}",
        }
        if API_VERSION is not None:
            headers["SendHub-Version"] = API_VERSION

        rbody, rcode = self.do_send_request(meth, abs_url, headers, params)

        LOGGER.debug(
            f"API request to {abs_url} returned response code: {rcode} & response body: {rbody}"
        )

        return rbody, rcode

    def interpret_response(self, rbody, rcode):
        """special case deleted because the response is empty"""
        if rcode == 204:
            resp = {"message": "OK"}
            return resp

        try:
            if isinstance(rbody, bytes):
                resp = json.loads(rbody.decode("utf-8"))
            else:
                resp = json.loads(rbody)
        except Exception as exp:
            raise APIError(
                message=f"Invalid response body from API: {rbody} (HTTP response code was {rcode!r})",
                dev_message="",
                code=rcode,
            ) from exp
        if not 200 <= rcode < 300:
            self.handle_api_error(rbody, rcode, resp)
        return resp

    def do_send_request(self, meth, abs_url, headers, params):
        """Sends request"""

        content = ""
        status_code = ""
        meth = meth.lower()
        data = None
        if meth in ("get", "delete"):
            if params:
                abs_url = self.build_url(abs_url, params)
        elif meth in ("post", "put", "patch"):
            abs_url = self.build_url(abs_url, params, True)

            new_params = {}
            for param in params:
                if param not in ("username", "password", "apiUsername", "apiPassword"):
                    new_params[param] = params[param]
            params = new_params

            data = self.encode_json(params)
        else:
            LOGGER.debug(f"Unrecognized HTTP method {meth}")
            raise APIConnectionError(
                f"Unrecognized HTTP method {meth}. This may indicate a bug in the SendHub bindings. Please contact support@sendhub.com for assistance."
            )

        kwargs = {}
        try:
            try:
                LOGGER.debug(
                    f"Sending HTTP request: method={meth}, url={abs_url}, headers={headers}, data={data}"
                )
                result = requests.request(
                    meth, abs_url, headers=headers, data=data, timeout=80, **kwargs
                )
            except TypeError as typ_err:
                LOGGER.debug(f"TypeError in requests.request: {typ_err}")
                raise TypeError(
                    f"Warning: It looks like your installed version of the `requests` library is not compatible. The underlying error was: {typ_err}"
                ) from typ_err

            content = result.content
            status_code = result.status_code
        except requests.exceptions.RequestException as exp_err:
            LOGGER.debug(f"RequestException in do_send_request: {exp_err}")
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
        LOGGER.debug(f"Request error: {msg}")
        raise APIConnectionError(msg)
