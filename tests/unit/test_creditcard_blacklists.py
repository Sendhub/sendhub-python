from unittest.mock import patch

import pytest
from sendhub.creditcard_blacklists import CreditCardBlacklist


class DummyCreditCardBlacklist(CreditCardBlacklist):
    def get_object(self, item_id):
        return {"id": item_id}

    def create_object(self, **kwargs):
        return kwargs

    def instance_url(self, item_id):
        return f"/cards/blacklist/{item_id}"

@pytest.fixture
def blacklist():
    return DummyCreditCardBlacklist()

def test_get_base_url():
    assert CreditCardBlacklist.get_base_url() == CreditCardBlacklist.get_base_url()

def test_class_url():
    assert CreditCardBlacklist.class_url() == "/api/v2/cards/blacklist"

@patch("sendhub.creditcard_blacklists.APIRequestor")
@patch("sendhub.creditcard_blacklists.SendHubObject")
def test_list_blacklist_no_query(mock_sendhub_obj, mock_api_requestor, blacklist):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": 1}, {"id": 2}]
    mock_sendhub_obj.construct_from.side_effect = lambda x: x
    result = blacklist.list_blacklist()
    assert result == [{"id": 1}, {"id": 2}]
    mock_instance.request.assert_called_once_with(meth="get", url="/api/v2/cards/blacklist", params={})

@patch("sendhub.creditcard_blacklists.APIRequestor")
@patch("sendhub.creditcard_blacklists.SendHubObject")
def test_list_blacklist_with_query(mock_sendhub_obj, mock_api_requestor, blacklist):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": 3}]
    mock_sendhub_obj.construct_from.side_effect = lambda x: x
    result = blacklist.list_blacklist("search")
    assert result == [{"id": 3}]
    mock_instance.request.assert_called_once_with(meth="get", url="/api/v2/cards/blacklist/search", params={})

def test_get_blacklist_item_success(blacklist):
    result = blacklist.get_blacklist_item(123)
    assert result == {"id": 123}

def test_get_blacklist_item_none(blacklist):
    with pytest.raises(ValueError):
        blacklist.get_blacklist_item(None)

def test_create_blacklist_item_success(blacklist):
    result = blacklist.create_blacklist_item("fingerprint123")
    assert result["fingerprint"] == "fingerprint123"

def test_create_blacklist_item_type_error(blacklist):
    with pytest.raises(TypeError):
        blacklist.create_blacklist_item(12345)

@patch("sendhub.creditcard_blacklists.APIRequestor")
def test_delete_blacklist_item_success(mock_api_requestor, blacklist):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    blacklist.delete_blacklist_item(123)
    mock_instance.request.assert_called_once_with("delete", "/cards/blacklist/123")

@patch("sendhub.creditcard_blacklists.APIRequestor")
def test_delete_blacklist_item_none(mock_api_requestor, blacklist):
    with pytest.raises(ValueError):
        blacklist.delete_blacklist_item(None)
