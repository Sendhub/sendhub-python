from unittest.mock import patch

import pytest

from sendhub.invoices import Invoice


class DummyInvoice(Invoice):
    def refresh_from(self, response):
        self._refreshed = response


@pytest.fixture
def invoice():
    return DummyInvoice()


def test_class_url():
    assert Invoice.class_url() == "/api/v2/invoices"


def test_get_base_url():
    assert Invoice.get_base_url() == Invoice.get_base_url()


@patch("sendhub.invoices.APIRequestor")
def test_process_minimal(mock_api_requestor, invoice):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "in_abc", "status": "paid"}

    result = invoice.process("in_abc", "pay")

    assert result is invoice
    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/invoice/process",
        {
            "invoice_id": "in_abc",
            "action": "pay",
            "correlation_id": "",
        },
    )
    assert invoice._refreshed == {"id": "in_abc", "status": "paid"}


@patch("sendhub.invoices.APIRequestor")
def test_process_with_guards(mock_api_requestor, invoice):
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {"id": "in_abc", "status": "void"}

    invoice.process(
        "in_abc",
        "void",
        correlation_id="corr-555",
        expected_customer_id="cus_abc",
        expected_currency="usd",
    )

    mock_instance.request.assert_called_once_with(
        "post",
        "/api/v2/invoice/process",
        {
            "invoice_id": "in_abc",
            "action": "void",
            "correlation_id": "corr-555",
            "expected_customer_id": "cus_abc",
            "expected_currency": "usd",
        },
    )


@patch("sendhub.invoices.APIRequestor")
def test_process_optional_guards_excluded_when_none(mock_api_requestor, invoice):
    """expected_customer_id / expected_currency absent from payload when not passed."""
    mock_instance = mock_api_requestor.return_value
    mock_instance.request.return_value = {}

    invoice.process("in_abc", "finalize")

    called_payload = mock_instance.request.call_args[0][2]
    assert "expected_customer_id" not in called_payload
    assert "expected_currency" not in called_payload
