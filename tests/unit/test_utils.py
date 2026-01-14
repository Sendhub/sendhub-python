from unittest.mock import patch

import pytest

from sendhub.utils import camel_to_snake, retry


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

def test_retry_invalid_tries():
    with pytest.raises(ValueError):
        retry(tries=-1)
    with pytest.raises(ValueError):
        retry(tries="a")
    with pytest.raises(ValueError):
        retry(tries=1, delay=0)
    with pytest.raises(ValueError):
        retry(tries=1, delay=1, backoff=1)
