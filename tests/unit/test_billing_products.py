from unittest.mock import patch

import pytest
from sendhub.billing_products import BillingProducts, Price


class DummyBillingProducts(BillingProducts):
    def get_list(self, **kwargs):
        return kwargs

    def get_object(self, product_id):
        return {"id": product_id}

    def create_object(self, **kwargs):
        return kwargs

    def update_object(self, obj_id, **kwargs):
        return {"obj_id": obj_id, **kwargs}

    def instance_url(self, product_id):
        return f"/products/{product_id}"

@pytest.fixture
def billing_products():
    return DummyBillingProducts()

def test_get_base_url():
    assert BillingProducts.get_base_url() == BillingProducts.get_base_url()

def test_class_url():
    assert BillingProducts.class_url() == "/api/v2/products"

def test_list_products_success(billing_products):
    result = billing_products.list_products(with_hidden=False, active_status="active")
    assert result["with_hidden"] == "0"
    assert result["active_status"] == "active"

def test_list_products_runtime_error():
    class ErrorBillingProducts(DummyBillingProducts):
        def get_list(self, **kwargs):
            raise Exception("fail")
    bp = ErrorBillingProducts()
    with pytest.raises(RuntimeError):
        bp.list_products()

def test_get_product_success(billing_products):
    result = billing_products.get_product(123)
    assert result == {"id": 123}

def test_get_product_none(billing_products):
    with pytest.raises(RuntimeError):
        billing_products.get_product(None)

def test_get_product_runtime_error():
    class ErrorBillingProducts(DummyBillingProducts):
        def get_object(self, product_id):
            raise Exception("fail")
    bp = ErrorBillingProducts()
    with pytest.raises(RuntimeError):
        bp.get_product(123)

def test_create_product_success(billing_products):
    prices = [
        Price(
            unitAmount=100,
            costPerText=0.01,
            voicePricePerMinute=0.05,
            messageOveragePrice=0.02,
            active=True,
            hidden=False,
            name="Standard",
            stripeNickname="std",
            currency="USD",
            priceMetadata={},
            productId=1,
            interval="month",
        )
    ]
    result = billing_products.create_product(
        name="Test",
        prices=prices,
        hippaPlan=True,
        shortcodeKeywords=True,
        autoAttendant=True,
        marketingLines=True,
        canEnableShortcode=True,
        dataExport=True,
        baseMessages=100,
        baseVoiceMinutes=200,
        maxUsers=10,
        maxMessages=1000,
        maxSmsRecipients=50,
        maxS2sRecipients=20,
        maxVoiceMinutes=500,
        maxConferenceLines=5,
        maxConferenceParticipants=10,
        maxApiRequests=100,
        maxBasicVmTranscriptions=10,
        maxPremiumVmTranscriptions=5,
        active=True,
        description="desc",
        statementDescriptor="statement",
        productMetadata={"meta": "value"},
        defaultPriceId=1,
        hidden=False,
        mailLogo=True,
    )
    assert result["name"] == "Test"
    assert result["prices"] == prices
    assert result["active"] is True
    assert result["description"] == "desc"
    assert result["statementDescriptor"] == "statement"
    assert result["productMetadata"] == {"meta": "value"}
    assert result["defaultPriceId"] == 1
    assert result["hidden"] is False
    assert result["mailLogo"] is True

def test_create_product_runtime_error():
    class ErrorBillingProducts(DummyBillingProducts):
        def create_object(self, **kwargs):
            raise ValueError("fail")
    bp = ErrorBillingProducts()
    prices = [
        Price(
            unitAmount=100,
            costPerText=0.01,
            voicePricePerMinute=0.05,
            messageOveragePrice=0.02,
            active=True,
            hidden=False,
            name="Standard",
            stripeNickname="std",
            currency="USD",
            priceMetadata={},
            productId=1,
            interval="month",
        )
    ]
    with pytest.raises(RuntimeError):
        bp.create_product(
            name="Test",
            prices=prices,
            hippaPlan=True,
            shortcodeKeywords=True,
            autoAttendant=True,
            marketingLines=True,
            canEnableShortcode=True,
            dataExport=True,
            baseMessages=100,
            baseVoiceMinutes=200,
            maxUsers=10,
            maxMessages=1000,
            maxSmsRecipients=50,
            maxS2sRecipients=20,
            maxVoiceMinutes=500,
            maxConferenceLines=5,
            maxConferenceParticipants=10,
            maxApiRequests=100,
            maxBasicVmTranscriptions=10,
            maxPremiumVmTranscriptions=5,
        )

def test_update_product(billing_products):
    result = billing_products.update_product(123, active=True)
    assert result["obj_id"] == 123
    assert result["active"] is True

@patch("sendhub.billing_products.APIRequestor")
def test_delete_product_success(mock_api_requestor, billing_products):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    billing_products.delete_product(123)
    mock_instance.request.assert_called_once_with("delete", "/products/123")

@patch("sendhub.billing_products.APIRequestor")
def test_delete_product_failure(mock_api_requestor, billing_products):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.side_effect = Exception("fail")
    with pytest.raises(Exception):
        billing_products.delete_product(123)


# ---------------------------------------------------------------------------
# Cache-aware: list_products_cached
# ---------------------------------------------------------------------------

@patch("sendhub.billing_products.APIRequestor")
def test_list_products_cached_200(mock_api_requestor, billing_products):
    """list_products_cached returns (products, etag, False) on 200."""
    mock_instance = mock_api_requestor.return_value
    products = [{"id": 1}, {"id": 2}]
    mock_instance.request.return_value = (products, 200, {"ETag": '"prod-v1"'})
    result, etag, not_modified = billing_products.list_products_cached(with_hidden=True, active_status="all")
    assert result == products
    assert etag == '"prod-v1"'
    assert not_modified is False
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs.get("extra_headers") is None  # no etag → no header
    assert call_kwargs["return_metadata"] is True


@patch("sendhub.billing_products.APIRequestor")
def test_list_products_cached_304(mock_api_requestor, billing_products):
    """list_products_cached returns (None, etag, True) on 304."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = (None, 304, {"ETag": '"prod-v1"'})
    result, etag, not_modified = billing_products.list_products_cached(etag='"prod-v1"')
    assert result is None
    assert not_modified is True
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs["extra_headers"] == {"If-None-Match": '"prod-v1"'}


@patch("sendhub.billing_products.APIRequestor")
def test_list_products_cached_passes_filters(mock_api_requestor, billing_products):
    """with_hidden and active_status are forwarded as query params."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = ([], 200, {})
    billing_products.list_products_cached(with_hidden=False, active_status="active")
    call_kwargs = mock_instance.request.call_args[1]
    assert call_kwargs["params"] == {"with_hidden": "0", "active_status": "active"}
