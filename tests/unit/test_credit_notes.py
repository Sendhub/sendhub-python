from unittest.mock import patch

import sendhub
from sendhub.credit_notes import CreditNote


def test_class_url():
    assert CreditNote.class_url() == "/api/v2/credit-notes"


def test_get_base_url():
    assert CreditNote.get_base_url() == CreditNote.get_base_url()


def test_credit_note_lazy_import():
    assert sendhub.CreditNote is CreditNote
    assert "CreditNote" in sendhub.__all__


@patch("sendhub.credit_notes.APIRequestor")
def test_create_refund_credit_note(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cn_123"}
    credit_note = CreditNote()

    result = credit_note.create(
        12,
        "in_123",
        refund_amount="2500",
        currency="usd",
        reason="duplicate",
        memo="Refund duplicate charge",
        metadata={"admin_user": "admin@example.com"},
    )

    assert result == {"id": "cn_123"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/12/credit-notes",
        {
            "invoice_id": "in_123",
            "currency": "usd",
            "refund_amount": 2500,
            "reason": "duplicate",
            "memo": "Refund duplicate charge",
            "metadata": {"admin_user": "admin@example.com"},
        },
    )


@patch("sendhub.credit_notes.APIRequestor")
def test_create_credit_note_supports_all_amount_fields(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cn_123"}
    credit_note = CreditNote()

    credit_note.create(
        12,
        "in_123",
        amount="5000",
        credit_amount="3000",
        out_of_band_amount="2000",
    )

    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/12/credit-notes",
        {
            "invoice_id": "in_123",
            "currency": "usd",
            "amount": 5000,
            "credit_amount": 3000,
            "out_of_band_amount": 2000,
        },
    )


@patch("sendhub.credit_notes.APIRequestor")
def test_list_credit_notes(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = [{"id": "cn_123"}]
    credit_note = CreditNote()

    result = credit_note.list(12, limit=25, offset=50)

    assert result == [{"id": "cn_123"}]
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/accounts/12/credit-notes",
        {"limit": 25, "offset": 50},
    )


@patch("sendhub.credit_notes.APIRequestor")
def test_get_credit_note(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cn_123"}
    credit_note = CreditNote()

    result = credit_note.get(12, "cn_123")

    assert result == {"id": "cn_123"}
    mock_instance.request.assert_called_once_with(
        "get",
        "/api/v2/accounts/12/credit-notes/cn_123",
        None,
    )


@patch("sendhub.credit_notes.APIRequestor")
def test_void_credit_note(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cn_123", "status": "void"}
    credit_note = CreditNote()

    result = credit_note.void(12, "cn_123", reason="requested")

    assert result == {"id": "cn_123", "status": "void"}
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/12/credit-notes/cn_123/void",
        {"reason": "requested"},
    )


@patch("sendhub.credit_notes.APIRequestor")
def test_void_credit_note_omits_reason(mock_api_requestor):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "cn_123", "status": "void"}
    credit_note = CreditNote()

    credit_note.void(12, "cn_123")

    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/accounts/12/credit-notes/cn_123/void",
        None,
    )
