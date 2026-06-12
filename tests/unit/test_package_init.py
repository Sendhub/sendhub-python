import sendhub
import sendhub.constants as constants

import importlib
import pytest


def test_early_stub_raises_runtime_error():
    stub = sendhub._early_stub("placeholder")
    with pytest.raises(RuntimeError, match="sendhub.placeholder used before sendhub finished initializing"):
        stub()


def test_package_dir_lists_lazy_imports():
    names = sendhub.__class__.__dir__(sendhub)
    assert "BillingAccount" in names
    assert "camel_to_snake" in names


def test_package_getattr_loads_synced_constant(monkeypatch):
    monkeypatch.delitem(sendhub.__dict__, "API_BASE", raising=False)
    assert sendhub.__class__.__getattr__(sendhub, "API_BASE") == constants.API_BASE


def test_package_setattr_mirrors_synced_constant():
    original = constants.USERNAME
    try:
        sendhub.__class__.__setattr__(sendhub, "USERNAME", "alice")
        assert constants.USERNAME == "alice"
        assert sendhub.__dict__["USERNAME"] == "alice"
    finally:
        sendhub.__class__.__setattr__(sendhub, "USERNAME", original)


def test_package_getattr_returns_existing_dict_value():
    assert sendhub.__class__.__getattr__(sendhub, "__all__") == sendhub.__dict__["__all__"]


def test_package_lazy_import_failure_has_helpful_message(monkeypatch):
    monkeypatch.setitem(sendhub._LAZY_IMPORTS, "BrokenImport", ".does_not_exist")
    try:
        with pytest.raises(AttributeError, match="failed to lazy-import 'BrokenImport'"):
            sendhub.__class__.__getattr__(sendhub, "BrokenImport")
    finally:
        del sendhub._LAZY_IMPORTS["BrokenImport"]


def test_force_import_populates_lazy_symbol(monkeypatch):
    monkeypatch.delitem(sendhub.__dict__, "CreditNote", raising=False)
    sendhub._force_import("CreditNote")
    assert sendhub.CreditNote.__name__ == "CreditNote"


def test_package_getattr_suppresses_synced_constant_import_failure(monkeypatch):
    original_import_module = importlib.import_module

    def broken_import_module(name, package=None):
        if name == "sendhub.constants":
            raise RuntimeError("boom")
        return original_import_module(name, package)

    monkeypatch.setattr(sendhub.importlib, "import_module", broken_import_module)
    monkeypatch.delitem(sendhub.__dict__, "API_BASE", raising=False)

    with pytest.raises(AttributeError):
        sendhub.__class__.__getattr__(sendhub, "API_BASE")


def test_package_setattr_tolerates_constant_import_failure(monkeypatch):
    original_import_module = importlib.import_module
    original_username = sendhub.__dict__.get("USERNAME")

    def broken_import_module(name, package=None):
        if name == "sendhub.constants":
            raise RuntimeError("boom")
        return original_import_module(name, package)

    monkeypatch.setattr(sendhub.importlib, "import_module", broken_import_module)
    try:
        sendhub.__class__.__setattr__(sendhub, "USERNAME", "local-only")
        assert sendhub.__dict__["USERNAME"] == "local-only"
    finally:
        sendhub.__class__.__setattr__(sendhub, "USERNAME", original_username)
