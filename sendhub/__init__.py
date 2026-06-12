# sendhub/__init__.py
"""
Lightweight package bootstrap:
- Keeps certain package-level names (constants) synced with sendhub.constants.
- Lazy-loads heavier submodules (APIRequestor, BillingPlans, utils functions, etc.)
This avoids circular imports while preserving the convenient `sendhub.Foo` API.
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from typing import Dict, Set

# Module path constants — centralised to avoid repeating string literals.
_MOD_CONSTANTS = ".constants"
_MOD_SENDHUB_ERROR = ".sendhub_error"
_MOD_UTILS = ".utils"

# -------------------------
# Configuration: which names to expose lazily and which to sync to constants
# -------------------------

# Lazy import map: public name -> relative module path (attribute name == key)
_LAZY_IMPORTS: dict[str, str] = {
    "APIRequestor": ".api_requestor",
    "APIResource": ".api_resource",
    "BillingAccount": ".billing_accounts",
    "BillingPlans": ".billing_plans",
    "BillingPrices": ".billing_prices",
    "BillingProducts": ".billing_products",
    "Coupon": ".coupons",
    "CreditNote": ".credit_notes",
    "CreditCardBlacklist": ".creditcard_blacklists",
    "Enterprise": ".enterprises",
    "Entitlement": ".entitlements",
    "EntitlementV2": ".entitlements",
    "Invoice": ".invoices",
    "PaymentMethod": ".payment_methods",
    "Profile": ".profile",
    "SendHubError": _MOD_SENDHUB_ERROR,
    "APIError": _MOD_SENDHUB_ERROR,
    "APIConnectionError": _MOD_SENDHUB_ERROR,
    "EntitlementError": _MOD_SENDHUB_ERROR,
    "InvalidRequestError": _MOD_SENDHUB_ERROR,
    "TryAgainLaterError": _MOD_SENDHUB_ERROR,
    "AuthenticationError": _MOD_SENDHUB_ERROR,
    "AuthorizationError": _MOD_SENDHUB_ERROR,
    "SendHubObject": ".sendhub_object",
    "StripeCustomer": ".stripe_customers",
    "StripePrice": ".stripe_prices",
    "StripeProduct": ".stripe_products",
    "StripeSubscription": ".stripe_subscriptions",
    # utils functions (loaded from .utils)
    "camel_to_snake": _MOD_UTILS,
    "convert_to_sendhub_object": _MOD_UTILS,
    "retry": _MOD_UTILS,
}

# Determine which names we should keep in sync with sendhub.constants.
# Prefer to auto-detect uppercase names from constants, but fall back to a minimal set.
try:
    _const_mod = importlib.import_module(__name__ + _MOD_CONSTANTS)
    _SYNC_TO_CONSTANTS: set[str] = {
        name for name in dir(_const_mod) if name.isupper() or name.startswith("_UNDERSCORER")
    }
    ENVIRONMENT_DETAIL = os.getenv('ENVIRONMENT_DETAIL', 'development')
except Exception:
    _SYNC_TO_CONSTANTS = {"USERNAME", "PASSWORD"}  # conservative fallback
    ENVIRONMENT_DETAIL = 'development'


# -------------------------
# Early placeholders to break circular imports
# -------------------------

def _early_stub(name: str):
    def _stub(*_a, **_kw):
        raise RuntimeError(
            f"sendhub.{name} used before sendhub finished initializing"
        )
    return _stub

# Pre-bind utils symbols so `from sendhub import X` never fails
camel_to_snake = _early_stub("camel_to_snake")
convert_to_sendhub_object = _early_stub("convert_to_sendhub_object")
retry = _early_stub("retry")


# -------------------------
# Module wrapper class
# -------------------------
class _Package(types.ModuleType):
    """
    Module wrapper that:
      - on attribute read: returns a synced constant (from constants) if requested,
        otherwise lazy-loads public symbols per _LAZY_IMPORTS, or falls back to module dict.
      - on attribute set: when writing a synced constant, mirror it into sendhub.constants.
    """

    def __getattr__(self, name: str):
        # 1) synced constants (uppercase-ish)
        if name in _SYNC_TO_CONSTANTS:
            try:
                const = importlib.import_module(__name__ + _MOD_CONSTANTS)
                if hasattr(const, name):
                    val = getattr(const, name)
                    # cache on module so subsequent lookups are fast
                    self.__dict__.setdefault(name, val)
                    return val
            except Exception:
                # fall through to other handlers
                pass

        # 2) lazy public symbols
        if name in _LAZY_IMPORTS:
            mod_path = _LAZY_IMPORTS[name]
            try:
                mod = importlib.import_module(mod_path, __name__)
                val = getattr(mod, name)
                # cache onto module for quick subsequent access
                self.__dict__[name] = val
                return val
            except Exception as e:
                # give a helpful AttributeError including the underlying problem
                raise AttributeError(
                    f"failed to lazy-import {name!r} from {mod_path!r}: {e}"
                ) from e

        # 3) existing module attributes
        if name in self.__dict__:
            return self.__dict__[name]

        # 4) not found
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __setattr__(self, name: str, value):
        # Mirror synced constants into the constants module when set on package.
        if name in _SYNC_TO_CONSTANTS:
            try:
                const = importlib.import_module(__name__ + _MOD_CONSTANTS)
                setattr(const, name, value)
            except Exception:
                # ignore write failures to constants (we still set on the module)
                pass
        # Always store the attribute on the module object itself.
        super().__setattr__(name, value)

    def __dir__(self):
        # Help IDEs and autocompletion by listing known lazy symbols + synced constants + actual attrs
        names = set(self.__dict__.keys()) | set(_LAZY_IMPORTS.keys()) | set(_SYNC_TO_CONSTANTS)
        return sorted(names)


# -------------------------
# Install wrapper into sys.modules
# -------------------------
# Replace current module object with our _Package instance so subsequent attribute access
# goes through the wrapper. We preserve existing globals (whatever Python has executed so far).
_current_mod = sys.modules[__name__]
_new_mod = _Package(__name__)
# copy the current module dict into our new object so existing names (while executing this file)
# are preserved.
_new_mod.__dict__.update(_current_mod.__dict__)

# preload any existing constant values into the package object (so they appear before assignment)
try:
    const = importlib.import_module(__name__ + _MOD_CONSTANTS)
    for nm in _SYNC_TO_CONSTANTS:
        if hasattr(const, nm):
            _new_mod.__dict__.setdefault(nm, getattr(const, nm))
except Exception:
    # if constants aren't importable at bootstrap, we'll lazy-load them later
    pass

# swap into sys.modules
sys.modules[__name__] = _new_mod

# From this point forward, writing to globals() below modifies the new module object.
# Use `mod = sys.modules[__name__]` if you need to refer to the module object explicitly.
mod = sys.modules[__name__]

# -------------------------
# Public API listing
# -------------------------
# Keep this list in sync with _LAZY_IMPORTS and with what your package intends to export.
mod.__dict__["__all__"] = [
    "APIRequestor",
    "APIResource",
    "BillingAccount",
    "BillingPlans",
    "BillingPrices",
    "BillingProducts",
    "CreditNote",
    "CreditCardBlacklist",
    "Enterprise",
    "Entitlement",
    "EntitlementV2",
    "Profile",
    "SendHubError",
    "SendHubObject",
    "camel_to_snake",
    "convert_to_sendhub_object",
    "retry",
    # constants (these are accessible through the sync mechanism)
    "API_BASE",
    "API_VERSION",
    "HTTP_LIB",
    "LOGGER",
    "PASSWORD",
    "USERNAME",
    "BILLING_BASE",
    "ENTITLEMENTS_BASE",
    "PROFILE_BASE",
    "_UNDERSCORER1",
    "__UNDERSCORER2",
]

# -------------------------
# Convenience: provide a small helper to force-populate a lazy symbol (for tests)
# -------------------------
def _force_import(name: str):
    """
    Force the lazy import of `name` (useful for tests or early initialization).
    Example: sendhub._force_import("BillingPlans")
    """
    getattr(mod, name)


# make helper available on the module
mod.__dict__["_force_import"] = _force_import


# -------------------------
# Late binding: replace stubs with real utils implementations
# -------------------------
try:
    from . import utils as _utils

    mod.__dict__["camel_to_snake"] = _utils.camel_to_snake
    mod.__dict__["convert_to_sendhub_object"] = _utils.convert_to_sendhub_object
    mod.__dict__["retry"] = _utils.retry

except Exception:
    # If utils still can't load, stubs remain (safe, explicit failure)
    pass



# -------------------------
# Module-level __getattr__ for direct imports
# -------------------------
def __getattr__(name):
    """
    Module-level __getattr__ to support direct imports (from sendhub import SomeClass).
    Delegates to the lazy loading logic in the module wrapper.
    """
    return getattr(mod, name)

# End of sendhub.__init__.py
