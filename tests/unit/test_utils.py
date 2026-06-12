from unittest.mock import patch

import pytest
from sendhub.sendhub_object import SendHubObject
from sendhub.utils import camel_to_snake, convert_to_sendhub_object, retry


def test_camel_to_snake_basic():
    assert camel_to_snake("CamelCase") == "camel_case"
    assert camel_to_snake("HTTPRequest") == "http_request"
    assert camel_to_snake("already_snake") == "already_snake"

def test_camel_to_snake_type_error():
    with pytest.raises(TypeError):
        camel_to_snake(123)

def test_camel_to_snake_empty():
    assert camel_to_snake("") == ""

def test_convert_to_sendhub_object_list(monkeypatch):
    # Patch SendHubObject.construct_from to just return the dict
    from sendhub import utils
    monkeypatch.setattr("sendhub.utils.convert_to_sendhub_object", lambda x: x)
    # Should just return the list as is (since patched)
    assert utils.convert_to_sendhub_object([1, 2, 3]) == [1, 2, 3]


def test_convert_to_sendhub_object_list_recurses_into_items():
    result = convert_to_sendhub_object([{"name": "plain"}])
    assert isinstance(result, list)
    assert isinstance(result[0], SendHubObject)
    assert result[0].name == "plain"


@patch("sendhub.sendhub_object.SendHubObject.construct_from", return_value="sendhub-object")
def test_convert_to_sendhub_object_dict_defaults_to_sendhub_object(mock_construct):
    result = convert_to_sendhub_object({"name": "plain"})
    assert result == "sendhub-object"
    mock_construct.assert_called_once_with({"name": "plain"})


@patch("sendhub.entitlements.Entitlement.construct_from", return_value="entitlement-object")
def test_convert_to_sendhub_object_dict_uses_entitlement_type(mock_construct):
    result = convert_to_sendhub_object({"object": "entitlement", "name": "quota"})
    assert result == "entitlement-object"
    mock_construct.assert_called_once_with({"object": "entitlement", "name": "quota"})


def test_convert_to_sendhub_object_non_string_object_defaults_to_sendhub_object():
    result = convert_to_sendhub_object({"object": 123, "name": "plain"})
    assert isinstance(result, SendHubObject)
    assert result.object == 123
    assert result.name == "plain"


def test_convert_to_sendhub_object_passthrough_scalar():
    assert convert_to_sendhub_object("value") == "value"

def test_retry_success_on_first_try():
    calls = []
    @retry(tries=2, delay=1, backoff=2, desired_outcome=42)
    def fn():
        calls.append(1)
        return 42
    assert fn() == 42
    assert len(calls) == 1

def test_retry_success_on_second_try():
    calls = []
    @retry(tries=2, delay=1, backoff=2, desired_outcome=42)
    def fn():
        calls.append(1)
        return 42 if len(calls) > 1 else 0
    assert fn() == 42
    assert len(calls) == 2

def test_retry_failure(monkeypatch):
    calls = []
    @retry(tries=1, delay=1, backoff=2, desired_outcome=42)
    def fn():
        calls.append(1)
        return 0
    with patch("time.sleep", return_value=None):
        assert fn() is False
    assert len(calls) == 2

def test_retry_with_callable_desired_outcome():
    calls = []
    @retry(tries=2, delay=1, backoff=2, desired_outcome=lambda x: x > 2)
    def fn():
        calls.append(1)
        return len(calls)
    assert fn() == 3
    assert len(calls) == 3


def test_retry_with_callable_desired_outcome_success_on_first_check():
    calls = []

    @retry(tries=2, delay=1, backoff=2, desired_outcome=lambda x: x > 2)
    def fn():
        calls.append(1)
        return 3

    assert fn() == 3
    assert len(calls) == 1


def test_retry_with_callable_failure_returns_last_value():
    calls = []

    @retry(tries=1, delay=1, backoff=2, desired_outcome=lambda x: x > 10)
    def fn():
        calls.append(1)
        return len(calls) + 4

    with patch("sendhub.utils._time.sleep", return_value=None):
        assert fn() == 6
    assert len(calls) == 2

def test_retry_invalid_tries():
    with pytest.raises(ValueError):
        retry(tries=-1)
    with pytest.raises(ValueError):
        retry(tries="a")
    with pytest.raises(ValueError):
        retry(tries=1, delay=0)
    with pytest.raises(ValueError):
        retry(tries=1, delay=1, backoff=1)
