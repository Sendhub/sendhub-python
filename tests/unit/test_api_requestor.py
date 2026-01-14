import pytest
import json
import datetime
from unittest.mock import patch, MagicMock
from sendhub.api_requestor import APIRequestor
from sendhub.sendhub_error import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    AuthorizationError,
    InvalidRequestError,
    TryAgainLaterError,
)

def test_api_url_default_base():
    req = APIRequestor()
    req.api_base = None
    assert req.api_url("foo") == f"https://api.sendhub.comfoo/"

def test_api_url_custom_base():
    req = APIRequestor()
    req.api_base = "http://localhost/"
    assert req.api_url("bar") == "http://localhost/bar/"

def test_api_url_type_error():
    req = APIRequestor()
    with pytest.raises(TypeError):
        req.api_url(123)

def test_utf8_returns_value():
    assert APIRequestor.utf8("abc") == "abc"
    assert APIRequestor.utf8(123) == 123

def test_encode_datetime_success():
    dt = datetime.datetime(2023, 1, 2, 3, 4, 5)
    assert APIRequestor.encode_datetime(dt) == "2023-01-02T03:04:05"

def test_encode_datetime_type_error():
    with pytest.raises(TypeError):
        APIRequestor.encode_datetime("not a datetime")

def test_encode_list_success():
    assert APIRequestor.encode_list([1, 2, 3]) == "1,2,3"

def test_encode_list_type_error():
    with pytest.raises(TypeError):
        APIRequestor.encode_list("notalist")

def test_encode_inner_encodes_types():
    dt = datetime.datetime(2023, 1, 2, 3, 4, 5)
    d = {"a": [1, 2], "b": dt, "c": "x"}
    result = APIRequestor._encode_inner(d)
    assert result["a"] == "1,2"
    assert result["b"] == "2023-01-02T03:04:05"
    assert result["c"] == "x"

def test_encode_inner_type_error():
    with pytest.raises(TypeError):
        APIRequestor._encode_inner("notadict")

def test_encode_and_encode_json():
    d = {"a": [1, 2]}
    urlencoded = APIRequestor.encode(d)
    assert "a=1%2C2" in urlencoded
    jsoned = APIRequestor.encode_json(d)
    assert '"a": "1,2"' in jsoned

def test_build_url_basic():
    url = "http://foo"
    params = {"a": 1}
    result = APIRequestor.build_url(url, params)
    assert result.startswith("http://foo?")
    assert "a=1" in result

def test_build_url_with_query():
    url = "http://foo?x=1"
    params = {"a": 1}
    result = APIRequestor.build_url(url, params)
    assert result.startswith("http://foo?x=1&")
    assert "a=1" in result

def test_build_url_auth_params_only():
    url = "http://foo"
    params = {"username": "u", "password": "p", "other": "x"}
    result = APIRequestor.build_url(url, params, auth_params_only=True)
    assert "username=u" in result
    assert "password=p" in result
    assert "other" not in result

def test_build_url_type_errors():
    with pytest.raises(TypeError):
        APIRequestor.build_url(123, {}, False)
    with pytest.raises(TypeError):
        APIRequestor.build_url("url", "notadict", False)

@patch("sendhub.api_requestor.USERNAME", "user")
@patch("sendhub.api_requestor.PASSWORD", "pass")
@patch("sendhub.api_requestor.LOGGER")
def test_request_success(mock_logger):
    req = APIRequestor()
    with patch.object(req, "perform_request", return_value=('{"ok": true}', 200)), \
         patch.object(req, "interpret_response", return_value={"ok": True}):
        result = req.request("get", "/foo")
        assert result == {"ok": True}

@patch("sendhub.api_requestor.USERNAME", None)
@patch("sendhub.api_requestor.PASSWORD", None)
@patch("sendhub.api_requestor.LOGGER")
def test_request_missing_auth(mock_logger):
    req = APIRequestor()
    with pytest.raises(AuthenticationError):
        req.request("get", "/foo")

@patch("sendhub.api_requestor.USERNAME", "user")
@patch("sendhub.api_requestor.PASSWORD", "pass")
@patch("sendhub.api_requestor.LOGGER")
def test_request_api_error_on_retries(mock_logger):
    req = APIRequestor()
    with patch.object(req, "perform_request", side_effect=APIError("fail")), \
         patch.object(req, "interpret_response", return_value={"fail": True}):
        with pytest.raises(APIError):
            req.request("get", "/foo")

def test_handle_api_error_invalid_response():
    with pytest.raises(APIError):
        APIRequestor.handle_api_error("body", 400, None)

def test_handle_api_error_invalid_request():
    resp = {"message": "msg", "dev_message": "dev", "code": 400, "more_info": "info"}
    with pytest.raises(InvalidRequestError):
        APIRequestor.handle_api_error("body", 400, resp)

def test_handle_api_error_authentication():
    resp = {"message": "msg", "dev_message": "dev", "code": 401, "more_info": "info"}
    with pytest.raises(AuthenticationError):
        APIRequestor.handle_api_error("body", 401, resp)

def test_handle_api_error_authorization():
    resp = {"message": "msg", "dev_message": "dev", "code": 403, "more_info": "info"}
    with pytest.raises(AuthorizationError):
        APIRequestor.handle_api_error("body", 403, resp)

def test_handle_api_error_try_again_later():
    resp = {"message": "Try again later", "dev_message": "dev", "code": 409, "more_info": "info"}
    with pytest.raises(TryAgainLaterError):
        APIRequestor.handle_api_error("body", 409, resp)

def test_handle_api_error_api_error():
    resp = {"message": "msg", "dev_message": "dev", "code": 500, "more_info": "info"}
    with pytest.raises(APIError):
        APIRequestor.handle_api_error("body", 500, resp)

def test_perform_request_internal_and_external(monkeypatch):
    req = APIRequestor()
    req.api_base = "http://base/"
    # Test INTERNAL_API True and False
    monkeypatch.setattr("sendhub.api_requestor.INTERNAL_API", True)
    monkeypatch.setattr("sendhub.api_requestor.USERNAME", "user")
    monkeypatch.setattr("sendhub.api_requestor.PASSWORD", "pass")
    with patch.object(req, "api_url", return_value="http://base/foo"), \
         patch.object(req, "do_send_request", return_value=('{"ok": true}', 200)), \
         patch("sendhub.api_requestor.VERSION", "1.0"):
        req.perform_request("get", "foo", {"a": 1})

    monkeypatch.setattr("sendhub.api_requestor.INTERNAL_API", False)
    with patch.object(req, "api_url", return_value="http://base/foo"), \
         patch.object(req, "do_send_request", return_value=('{"ok": true}', 200)), \
         patch("sendhub.api_requestor.VERSION", "1.0"):
        req.perform_request("get", "foo", {"a": 1})

def test_interpret_response_204():
    req = APIRequestor()
    assert req.interpret_response("anything", 204) == {"message": "OK"}

def test_interpret_response_json_bytes():
    req = APIRequestor()
    data = json.dumps({"foo": "bar"}).encode("utf-8")
    assert req.interpret_response(data, 200) == {"foo": "bar"}

def test_interpret_response_json_str():
    req = APIRequestor()
    data = json.dumps({"foo": "bar"})
    assert req.interpret_response(data, 200) == {"foo": "bar"}

def test_interpret_response_invalid_json():
    req = APIRequestor()
    with pytest.raises(APIError):
        req.interpret_response("notjson", 200)

def test_interpret_response_error_code(monkeypatch):
    req = APIRequestor()
    resp = json.dumps({"message": "fail"})
    with patch.object(APIRequestor, "handle_api_error", side_effect=APIError("fail")):
        with pytest.raises(APIError):
            req.interpret_response(resp, 400)

@patch("sendhub.api_requestor.requests.request")
@patch("sendhub.api_requestor.LOGGER")
def test_do_send_request_get(mock_logger, mock_request):
    req = APIRequestor()
    mock_result = MagicMock()
    mock_result.content = b"abc"
    mock_result.status_code = 200
    mock_request.return_value = mock_result
    content, status = req.do_send_request("get", "url", {}, {"a": 1})
    assert content == b"abc"
    assert status == 200

@patch("sendhub.api_requestor.requests.request")
@patch("sendhub.api_requestor.LOGGER")
def test_do_send_request_post(mock_logger, mock_request):
    req = APIRequestor()
    mock_result = MagicMock()
    mock_result.content = b"abc"
    mock_result.status_code = 201
    mock_request.return_value = mock_result
    content, status = req.do_send_request("post", "url", {}, {"a": 1})
    assert content == b"abc"
    assert status == 201

@patch("sendhub.api_requestor.requests.request")
@patch("sendhub.api_requestor.LOGGER")
def test_do_send_request_type_error(mock_logger, mock_request):
    req = APIRequestor()
    mock_request.side_effect = TypeError("fail")
    with pytest.raises(TypeError):
        req.do_send_request("get", "url", {}, {"a": 1})

@patch("sendhub.api_requestor.requests.request")
@patch("sendhub.api_requestor.LOGGER")
def test_do_send_request_request_exception(mock_logger, mock_request):
    req = APIRequestor()
    import requests
    mock_request.side_effect = requests.exceptions.RequestException("fail")
    with patch.object(req, "handle_request_error", side_effect=APIConnectionError("fail")):
        with pytest.raises(APIConnectionError):
            req.do_send_request("get", "url", {}, {"a": 1})

@patch("sendhub.api_requestor.LOGGER")
def test_do_send_request_unrecognized_method(mock_logger):
    req = APIRequestor()
    with pytest.raises(APIConnectionError):
        req.do_send_request("patchy", "url", {}, {"a": 1})

@patch("sendhub.api_requestor.LOGGER")
def test_handle_request_error_requests_exception(mock_logger):
    import requests
    exc = requests.exceptions.RequestException("fail")
    with pytest.raises(APIConnectionError) as e:
        APIRequestor.handle_request_error(exc)
    assert "RequestException" in str(e.value)

@patch("sendhub.api_requestor.LOGGER")
def test_handle_request_error_other_exception(mock_logger):
    exc = ValueError("fail")
    with pytest.raises(APIConnectionError) as e:
        APIRequestor.handle_request_error(exc)
    assert "ValueError" in str(e.value)
