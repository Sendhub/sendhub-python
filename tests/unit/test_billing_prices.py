from unittest.mock import patch

import pytest

from sendhub.billing_prices import BillingPrices, CustomDict


class DummyBillingPrices(BillingPrices):
    def get_list(self, **kwargs):
        return kwargs

    def get_object(self, price_id):
        return {"id": price_id}

    def create_object(self, **kwargs):
        return kwargs

    def update_object(self, obj_id, **kwargs):
        return {"obj_id": obj_id, **kwargs}

    def instance_url(self, price_id):
        return f"/prices/{price_id}"

@pytest.fixture
def billing_prices():
    return DummyBillingPrices()

def test_get_base_url():
    assert BillingPrices.get_base_url() == BillingPrices.get_base_url()

def test_class_url():
    assert BillingPrices.class_url() == "/api/v2/prices"

def test_list_prices(billing_prices):
    result = billing_prices.list_prices(with_hidden=False, active_status="active")
    assert result["with_hidden"] == "0"
    assert result["active_status"] == "active"

def test_get_price(billing_prices):
    result = billing_prices.get_price(123)
    assert result == {"id": 123}

def test_create_price(billing_prices):
    metadata: CustomDict = {"meta": "value"}
    result = billing_prices.create_price(
        unitAmount=100,
        costPerText=0.01,
        voicePricePerMinute=0.05,
        messageOveragePrice=0.02,
        active=True,
        hidden=False,
        name="Standard",
        stripeNickname="std",
        currency="USD",
        productId=1,
        interval="month",
        priceMetadata=metadata,
    )
    assert result["unitAmount"] == 100
    assert result["costPerText"] == 0.01
    assert result["voicePricePerMinute"] == 0.05
    assert result["messageOveragePrice"] == 0.02
    assert result["active"] is True
    assert result["hidden"] is False
    assert result["name"] == "Standard"
    assert result["stripeNickname"] == "std"
    assert result["currency"] == "USD"
    assert result["productId"] == 1
    assert result["interval"] == "month"
    assert result["priceMetadata"] == metadata

def test_update_price(billing_prices):
    result = billing_prices.update_price(123, active=True)
    assert result["obj_id"] == 123
    assert result["active"] is True

@patch("sendhub.billing_prices.APIRequestor")
def test_delete_price_success(mock_api_requestor, billing_prices):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    billing_prices.delete_price(123)
    mock_instance.request.assert_called_once_with("delete", "/prices/123")

@patch("sendhub.billing_prices.APIRequestor")
def test_delete_price_failure(mock_api_requestor, billing_prices):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(RuntimeError):
        billing_prices.delete_price(123)
