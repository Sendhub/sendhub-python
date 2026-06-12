
from sendhub.sendhub_error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    AuthorizationError,
    EntitlementError,
    InvalidRequestError,
    SendHubError,
    TryAgainLaterError,
)


def test_sendhub_error_defaults():
    err = SendHubError()
    assert isinstance(err, Exception)
    assert err.dev_message == ""
    assert err.code == -1
    assert err.more_info == ""

def test_sendhub_error_custom_values():
    err = SendHubError("msg", "dev", 42, "info")
    assert err.args[0] == "msg"
    assert err.dev_message == "dev"
    assert err.code == 42
    assert err.more_info == "info"

def test_api_error_inheritance():
    err = APIError("api error")
    assert isinstance(err, SendHubError)
    assert isinstance(err, APIError)
    assert err.args[0] == "api error"

def test_api_connection_error_inheritance():
    err = APIConnectionError("conn error")
    assert isinstance(err, SendHubError)
    assert isinstance(err, APIConnectionError)
    assert err.args[0] == "conn error"

def test_entitlement_error_custom():
    err = EntitlementError("entitlement", "dev", 401, "info")
    assert isinstance(err, SendHubError)
    assert isinstance(err, EntitlementError)
    assert err.args[0] == "entitlement"
    assert err.dev_message == "dev"
    assert err.code == 401
    assert err.more_info == "info"

def test_invalid_request_error_custom():
    err = InvalidRequestError("invalid", "dev", 400, "info")
    assert isinstance(err, SendHubError)
    assert isinstance(err, InvalidRequestError)
    assert err.args[0] == "invalid"
    assert err.dev_message == "dev"
    assert err.code == 400
    assert err.more_info == "info"

def test_try_again_later_error_custom():
    err = TryAgainLaterError("try again", "dev", 503, "info")
    assert isinstance(err, SendHubError)
    assert isinstance(err, TryAgainLaterError)
    assert err.args[0] == "try again"
    assert err.dev_message == "dev"
    assert err.code == 503
    assert err.more_info == "info"

def test_authentication_error_inheritance():
    err = AuthenticationError("auth error")
    assert isinstance(err, SendHubError)
    assert isinstance(err, AuthenticationError)
    assert err.args[0] == "auth error"

def test_authorization_error_inheritance():
    err = AuthorizationError("authz error")
    assert isinstance(err, SendHubError)
    assert isinstance(err, AuthorizationError)
    assert err.args[0] == "authz error"
