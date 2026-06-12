from unittest.mock import patch

import pytest
from sendhub.api_resource import APIResource
from sendhub.sendhub_error import InvalidRequestError


class DummyResource(APIResource):
    @classmethod
    def class_name(cls):
        return "dummyresource"

@pytest.fixture
def resource():
    return DummyResource()

def test_get_base_url():
    assert APIResource.get_base_url() == APIResource.get_base_url()


def test_instance_url_with_get_valid(resource):
    resource.id = "xyz"
    url = resource.instance_url()
    assert url == "/v1/dummyresources/xyz"

@patch("sendhub.api_resource.APIRequestor")
def test_get_object_success(mock_api_requestor, resource):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": 123}
    with patch.object(resource, "refresh_from") as mock_refresh:
        result = resource.get_object(123)
        assert result is resource
        mock_refresh.assert_called_once_with({"id": 123})
        assert resource._id == 123

def test_get_object_none(resource):
    with pytest.raises(ValueError):
        resource.get_object(None)

@patch("sendhub.api_resource.APIRequestor")
@patch("sendhub.api_resource.SendHubObject")
def test_get_list(mock_sendhub_obj, mock_api_requestor, resource):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": 1}, {"id": 2}]
    mock_sendhub_obj.construct_from.side_effect = lambda x: x
    result = resource.get_list(foo="bar")
    assert result == [{"id": 1}, {"id": 2}]
    mock_instance.request.assert_called_once_with(meth="get", url=resource.class_url(), params={"foo": "bar"})

@patch("sendhub.api_resource.APIRequestor")
def test_create_object(mock_api_requestor, resource):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": 1}
    with patch.object(resource, "refresh_from") as mock_refresh:
        result = resource.create_object(foo="bar")
        assert result is resource
        mock_refresh.assert_called_once_with({"id": 1})

@patch("sendhub.api_resource.APIRequestor")
def test_update_object_success(mock_api_requestor, resource):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": 2}
    with patch.object(resource, "refresh_from") as mock_refresh:
        result = resource.update_object(2, foo="baz")
        assert result is resource
        mock_refresh.assert_called_once_with({"id": 2})
        assert resource._id == 2

def test_update_object_none(resource):
    with pytest.raises(ValueError):
        resource.update_object(None, foo="baz")

def test_instance_url_with_id(resource):
    url = resource.instance_url("abc")
    assert url == "/v1/dummyresources/abc"

def test_instance_url_with_get(resource):
    resource._id = "xyz"
    resource.id = "xyz"
    url = resource.instance_url()
    assert url == "/v1/dummyresources/xyz"
    resource._id = "xyz"
    resource.__dict__["id"] = "xyz"

def test_instance_url_invalid(resource):
    with pytest.raises(InvalidRequestError):
        resource.instance_url(None)

def test_class_name_not_implemented():
    with pytest.raises(NotImplementedError):
        APIResource.class_name()

def test_class_url():
    class Dummy(APIResource):
        @classmethod
        def class_name(cls):
            return "dummy"
    assert Dummy.class_url() == "/v1/dummys"


# ---------------------------------------------------------------------------
# Cache-aware: get_cached
# ---------------------------------------------------------------------------

@patch("sendhub.api_resource.APIRequestor")
def test_get_cached_200_no_etag(mock_api_requestor, resource):
    """get_cached with no etag returns (payload, new_etag, False)."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"id": 7}, 200, {"ETag": '"v1"'})
    with patch.object(resource, "refresh_from"):
        payload, new_etag, not_modified = resource.get_cached(7)

    assert payload == {"id": 7}
    assert new_etag == '"v1"'
    assert not_modified is False
    # No If-None-Match header should be sent when etag is absent
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs.get("extra_headers") is None
    assert call_kwargs["return_metadata"] is True


@patch("sendhub.api_resource.APIRequestor")
def test_get_cached_200_with_etag(mock_api_requestor, resource):
    """get_cached sends If-None-Match when etag is provided."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ({"id": 8}, 200, {"ETag": '"v2"'})
    with patch.object(resource, "refresh_from"):
        payload, new_etag, not_modified = resource.get_cached(8, etag='"v1"')

    assert not_modified is False
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs["extra_headers"] == {"If-None-Match": '"v1"'}


@patch("sendhub.api_resource.APIRequestor")
def test_get_cached_304(mock_api_requestor, resource):
    """get_cached with 304 returns (None, etag, True) without calling refresh_from."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"v1"'})
    with patch.object(resource, "refresh_from") as mock_refresh:
        payload, new_etag, not_modified = resource.get_cached(9, etag='"v1"')

    assert payload is None
    assert new_etag == '"v1"'
    assert not_modified is True
    mock_refresh.assert_not_called()


def test_get_cached_none_obj_id(resource):
    with pytest.raises(ValueError):
        resource.get_cached(None)


# ---------------------------------------------------------------------------
# Cache-aware: get_list_cached
# ---------------------------------------------------------------------------

@patch("sendhub.api_resource.APIRequestor")
def test_get_list_cached_200_no_etag(mock_api_requestor, resource):
    """get_list_cached returns (items, new_etag, False) on 200."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ([{"id": 1}, {"id": 2}], 200, {"ETag": '"list-v1"'})
    items, new_etag, not_modified = resource.get_list_cached()

    assert len(items) == 2
    assert new_etag == '"list-v1"'
    assert not_modified is False
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs.get("extra_headers") is None


@patch("sendhub.api_resource.APIRequestor")
def test_get_list_cached_304(mock_api_requestor, resource):
    """get_list_cached returns (None, etag, True) on 304."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"list-v1"'})
    items, new_etag, not_modified = resource.get_list_cached(etag='"list-v1"')

    assert items is None
    assert new_etag == '"list-v1"'
    assert not_modified is True
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs["extra_headers"] == {"If-None-Match": '"list-v1"'}


@patch("sendhub.api_resource.APIRequestor")
def test_get_list_cached_with_params(mock_api_requestor, resource):
    """Extra kwargs are forwarded as query params."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ([{"id": 3}], 200, {})
    resource.get_list_cached(foo="bar")

    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs.get("params") == {"foo": "bar"}
