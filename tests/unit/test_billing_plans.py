from unittest.mock import patch

import pytest

from sendhub.billing_plans import BillingPlans


class DummyBillingPlans(BillingPlans):
    def get_list(self, **kwargs):
        return kwargs

    def get_object(self, plan_id):
        return {"id": plan_id}

    def create_object(self, **kwargs):
        return kwargs

    def update_object(self, obj_id, **kwargs):
        return {"obj_id": obj_id, **kwargs}

    def instance_url(self, plan_id):
        return f"/plans/{plan_id}"

@pytest.fixture
def billing_plans():
    return DummyBillingPlans()

def test_get_base_url():
    assert BillingPlans.get_base_url() == BillingPlans.get_base_url()

def test_class_url():
    assert BillingPlans.class_url() == "/api/v2/plans"

def test_list_plans(billing_plans):
    result = billing_plans.list_plans(with_hidden=False, active_status="active")
    assert result["with_hidden"] == "0"
    assert result["active_status"] == "active"

def test_get_plan_success(billing_plans):
    result = billing_plans.get_plan(123)
    assert result == {"id": 123}

def test_get_plan_none(billing_plans):
    with pytest.raises(ValueError):
        billing_plans.get_plan(None)

def test_create_plan(billing_plans):
    result = billing_plans.create_plan(
        plan_type_id=1,
        name="Test",
        description="desc",
        cost=10,
        max_users=100,
        max_messages=1000,
        max_sms_recipients=50,
        max_s2s_recipients=20,
        shortcode_keywords="kw",
        can_enable_shortcode=True,
        max_voice_minutes=500,
        max_conference_lines=5,
        max_conference_participants=10,
        marketing_lines="ml",
        auto_attendant=True,
        max_api_requests=100,
        max_basic_vm_transcriptions=10,
        max_premium_vm_transcriptions=5,
        data_export=True,
        hippa_plan=False,
        mail_logo=True,
        base_messages=100,
        base_voice_minutes=200,
        message_overage_price=2,
        voice_price_per_minute=0.5,
    )
    assert result["planTypeId"] == 1
    assert result["name"] == "Test"
    assert result["cost"] == "10"
    assert result["msgOveragePrice"] == "2"
    assert result["voicePricePerMinute"] == "0.5"

def test_update_plan_success(billing_plans):
    result = billing_plans.update_plan(123, active=True)
    assert result["obj_id"] == 123
    assert result["active"] is True

def test_update_plan_none(billing_plans):
    with pytest.raises(ValueError):
        billing_plans.update_plan(None, active=True)

@patch("sendhub.billing_plans.APIRequestor")
def test_delete_plan_success(mock_api_requestor, billing_plans):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = None
    billing_plans.delete_plan(123)
    mock_instance.request.assert_called_once_with("delete", "/plans/123")

@patch("sendhub.billing_plans.APIRequestor")
def test_delete_plan_none(mock_api_requestor, billing_plans):
    with pytest.raises(ValueError):
        billing_plans.delete_plan(None)
