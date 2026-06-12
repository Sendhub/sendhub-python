from unittest.mock import patch

import pytest
from sendhub.coupons import Coupon


class DummyCoupon(Coupon):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def coupon():
    return DummyCoupon()


def test_class_url():
    assert Coupon.class_url() == "/api/v2/bridge/coupons"


def test_get_base_url():
    assert Coupon.get_base_url() == Coupon.get_base_url()


@patch("sendhub.coupons.APIRequestor")
def test_get_coupon(mock_api_requestor, coupon):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "SAVE10", "percent_off": 10}

    result = coupon.get_coupon("SAVE10")

    assert result is coupon
    mock_instance.request.assert_called_once_with(
        "get", "/api/v2/bridge/coupons/SAVE10"
    )
    assert coupon._refreshed == {"id": "SAVE10", "percent_off": 10}
