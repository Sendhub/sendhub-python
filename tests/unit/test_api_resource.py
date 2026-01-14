from unittest.mock import patch

import pytest

from sendhub.api_resource import APIResource
from sendhub.sendhub_error import InvalidRequestError
from sendhub.sendhub_object import SendHubObject


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
