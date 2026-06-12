sendhub-python
=========

SendHub Python bindings for [SendHub](https://sendhub.com/).

Table Of Contents
-----------------

- [sendhub-python](#sendhub-python)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [What's New](#whats-new)
    - [Version 0.26.05 (Latest)](#version-02605-latest)
    - [Python Packaging Enhancements](#python-packaging-enhancements)
    - [Enhanced Authentication Session Management](#enhanced-authentication-session-management)
    - [Cache-Aware Billing Reads](#cache-aware-billing-reads)
  - [Cache-Aware Reads Usage](#cache-aware-reads-usage)
    - [First fetch — store the ETag](#first-fetch--store-the-etag)
    - [Subsequent fetch — revalidate with If-None-Match](#subsequent-fetch--revalidate-with-if-none-match)
    - [Other cached helpers](#other-cached-helpers)
    - [Low-level transport](#low-level-transport)
  - [Installation](#installation)
  - [Building \& Packaging](#building--packaging)
  - [Testing The Build](#testing-the-build)
  - [Development Workflow](#development-workflow)
  - [Testing \& Quality](#testing--quality)
    - [Unit Testing](#unit-testing)
    - [Linting \& Formatting](#linting--formatting)
    - [.gitignore Hygiene](#gitignore-hygiene)
  - [Integration \& E2E Testing](#integration--e2e-testing)
  - [Project Layout](#project-layout)
  - [License](#license)
  - [Contributing](#contributing)

About
-----------------

**SendHub - Python** is an library designed for internalcommunication between sendhub's own application

- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.
- **Testability**: Improved separation of concerns makes the code more testable.
- **Maintainability**: Clear structure and separation facilitate better management of the codebase.

What's New
-----------------

### Version 0.26.05 (Latest)

### Python Packaging Enhancements

- `pyproject.toml`: Earlier settings.py was being used to build the package from repo, now pyproject.toml will be used.

### Enhanced Authentication Session Management

- **Support for Python 3.13**: Keeping the implemented logic same, the code has been improved to utilize python 3.13
- **New endpoints under Billing Accounts**: To accomodate the stripe changes the billing account has been enhanced.

### Cache-Aware Billing Reads

- **Conditional GET support in `APIRequestor`**: `request()` now accepts
  `extra_headers` (merged into the outgoing request without overwriting auth
  headers) and `return_metadata` (returns a `(payload, status_code,
  response_headers)` 3-tuple instead of just the payload).
- **`304 Not Modified` handling**: `interpret_response` short-circuits on 304
  and returns `None`, so callers can detect cache hits without an exception.
- **`APIResource` helpers**: `get_cached(obj_id, etag=None)` and
  `get_list_cached(etag=None, **params)` wrap the transport layer so
  higher-level classes don't have to build `If-None-Match` logic themselves.
- **`BillingAccount` cached reads**: `get_account_cached`,
  `get_subscription_cached`, `get_plan_cached`, `get_plan_history_cached`, and
  `get_account_state_cached` all accept an optional `etag` and return
  `(payload, new_etag, not_modified)`.
- **`BillingProducts` / `BillingPrices`**: `list_products_cached` and
  `list_prices_cached` follow the same convention.

> **Migration Note**: This release maintains full backward compatibility. No breaking changes were introduced.

Cache-Aware Reads Usage
-----------------

All existing calls continue to work unchanged.  The new `*_cached` helpers
and the `return_metadata` flag are strictly opt-in.

### First fetch — store the ETag

```python
from sendhub.billing_accounts import BillingAccount

ba = BillingAccount()

# Normal first fetch — capture the ETag from the response metadata
payload, etag, not_modified = ba.get_account_cached(enterprise_id=42)
# not_modified is False; payload contains the account data; etag is e.g. '"abc123"'
```

### Subsequent fetch — revalidate with If-None-Match

```python
payload, etag, not_modified = ba.get_account_cached(enterprise_id=42, etag=etag)

if not_modified:
    # Server replied 304 — use your local cached copy, nothing to update
    pass
else:
    # Server replied 200 with a fresh payload and possibly a new ETag
    process(payload)
```

### Other cached helpers

```python
# Subscription / payment data
payload, etag, nm = ba.get_subscription_cached(enterprise_id=42, etag=etag)

# Plan data
payload, etag, nm = ba.get_plan_cached(enterprise_id=42, etag=etag)

# Plan history (offset + limit forwarded as query params)
payload, etag, nm = ba.get_plan_history_cached(enterprise_id=42, offset=0, limit=20, etag=etag)

# Account state
payload, etag, nm = ba.get_account_state_cached(enterprise_id=42, etag=etag)

# Products
from sendhub.billing_products import BillingProducts
products, etag, nm = BillingProducts().list_products_cached(etag=etag)

# Prices
from sendhub.billing_prices import BillingPrices
prices, etag, nm = BillingPrices().list_prices_cached(etag=etag)
```

### Low-level transport

For cases not covered by the high-level helpers, `APIRequestor.request()` exposes
the same primitives directly:

```python
from sendhub.api_requestor import APIRequestor

req = APIRequestor()
req.api_base = "https://billing.example.com"

payload, status, headers = req.request(
    meth="get",
    url="/api/v2/some-endpoint",
    extra_headers={"If-None-Match": stored_etag},
    return_metadata=True,
)

new_etag = headers.get("ETag")
not_modified = status == 304
```

Installation
-----------------

From source (this repo):

```bash
# Clone the repository
git clone https://github.com/Sendhub/sendhub-python.git
cd sendhub-python

# Install dependencies + project in editable mode
pip install -e ".[dev]"
```

Building & Packaging
-----------------

We use [PEP 517/518](https://peps.python.org/pep-0518/) with `pyproject.toml`.
All modern build tools work, but the recommended one is [`build`](https://pypi.org/project/build/).

```bash
# Cleaning old builds
rm -rf dist build *.egg-info

# Installing build, setuptools, wheel
python -m pip install --upgrade build setuptools wheel

# Building wheel + source distribution
python -m build

# Checking the distribution contents
ls dist/
```

Testing The Build
-----------------

Installing into a fresh virtual environment to verify:

```bash
python -m venv .venv-test
source .venv-test/bin/activate

pip install dist/sendhub-*.whl

python -c "from importlib.metadata import version; print('Installed version:', version('sendhub'))"

deactivate
```

Development Workflow
-----------------

Format, lint, and test:

```bash
# auto-format
black .

# sort imports
isort .

# lint with ruff
ruff check .

# run tests
pytest
```

Optional: install all dev dependencies with

```bash
pip install -e ".[dev]"
```

Testing & Quality
-----------------

### Unit Testing

- All unit tests live under `tests/unit/`.
- Uses [pytest](https://docs.pytest.org/) with a modern, quiet, colored output configuration (see `pyproject.toml`).
- Run all tests:

  ```bash
  pytest
  ```

- Coverage:

  ```bash
  coverage run -m pytest
  coverage report -m sendhub/*.py
  ```

### Linting & Formatting

- [black](https://black.readthedocs.io/), [isort](https://pycqa.github.io/isort/), and [ruff](https://docs.astral.sh/ruff/) are used for code style and linting.
- Run all checks:

  ```bash
  black .
  isort .
  ruff check .
  ```

### .gitignore Hygiene

- The `.gitignore` is curated to exclude all test, coverage, linter, and build artifacts, as well as IDE and virtual environment folders.

Integration & E2E Testing
------------------------

- Integration and end-to-end (E2E) tests may require access to real or sandboxed external services (e.g., SendHub API, Stripe, etc.).
- For integration/E2E, configure credentials and endpoints for sandbox environments. Do not use production credentials.
- Clean up test data after runs to avoid polluting shared environments.
- See `pyproject.toml` for test discovery and output settings.

Project Layout
-----------------

```shell
$ tree -I venv
.
├── LICENSE
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── pytest.ini
├── ruff.toml
├── sendhub
│   ├── VERSION
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   ├── api_requestor.cpython-314.pyc
│   │   ├── api_resource.cpython-314.pyc
│   │   ├── billing_accounts.cpython-314.pyc
│   │   ├── billing_plans.cpython-314.pyc
│   │   ├── billing_prices.cpython-314.pyc
│   │   ├── billing_products.cpython-314.pyc
│   │   ├── constants.cpython-314.pyc
│   │   ├── coupons.cpython-314.pyc
│   │   ├── credit_notes.cpython-314.pyc
│   │   ├── creditcard_blacklists.cpython-314.pyc
│   │   ├── enterprises.cpython-314.pyc
│   │   ├── entitlements.cpython-314.pyc
│   │   ├── invoices.cpython-314.pyc
│   │   ├── payment_methods.cpython-314.pyc
│   │   ├── profile.cpython-314.pyc
│   │   ├── sendhub_error.cpython-314.pyc
│   │   ├── sendhub_object.cpython-314.pyc
│   │   ├── stripe_customers.cpython-314.pyc
│   │   ├── stripe_prices.cpython-314.pyc
│   │   ├── stripe_products.cpython-314.pyc
│   │   ├── stripe_subscriptions.cpython-314.pyc
│   │   ├── utils.cpython-314.pyc
│   │   └── version.cpython-314.pyc
│   ├── api_requestor.py
│   ├── api_resource.py
│   ├── billing_accounts.py
│   ├── billing_plans.py
│   ├── billing_prices.py
│   ├── billing_products.py
│   ├── constants.py
│   ├── coupons.py
│   ├── credit_notes.py
│   ├── creditcard_blacklists.py
│   ├── enterprises.py
│   ├── entitlements.py
│   ├── invoices.py
│   ├── payment_methods.py
│   ├── profile.py
│   ├── sendhub_error.py
│   ├── sendhub_object.py
│   ├── stripe_customers.py
│   ├── stripe_prices.py
│   ├── stripe_products.py
│   ├── stripe_subscriptions.py
│   ├── utils.py
│   └── version.py
└── tests
    └── unit
        ├── __pycache__
        │   ├── test_api_requestor.cpython-314-pytest-9.0.2.pyc
        │   ├── test_api_requestor.cpython-314-pytest-9.0.3.pyc
        │   ├── test_api_resource.cpython-314-pytest-9.0.2.pyc
        │   ├── test_api_resource.cpython-314-pytest-9.0.3.pyc
        │   ├── test_billing_accounts.cpython-314-pytest-9.0.2.pyc
        │   ├── test_billing_accounts.cpython-314-pytest-9.0.3.pyc
        │   ├── test_billing_accounts.cpython-314.pyc
        │   ├── test_billing_plans.cpython-314-pytest-9.0.2.pyc
        │   ├── test_billing_plans.cpython-314-pytest-9.0.3.pyc
        │   ├── test_billing_prices.cpython-314-pytest-9.0.2.pyc
        │   ├── test_billing_prices.cpython-314-pytest-9.0.3.pyc
        │   ├── test_billing_products.cpython-314-pytest-9.0.2.pyc
        │   ├── test_billing_products.cpython-314-pytest-9.0.3.pyc
        │   ├── test_constants.cpython-314-pytest-9.0.3.pyc
        │   ├── test_constants.cpython-314.pyc
        │   ├── test_coupons.cpython-314-pytest-9.0.2.pyc
        │   ├── test_coupons.cpython-314-pytest-9.0.3.pyc
        │   ├── test_credit_notes.cpython-314-pytest-9.0.3.pyc
        │   ├── test_credit_notes.cpython-314.pyc
        │   ├── test_creditcard_blacklists.cpython-314-pytest-9.0.2.pyc
        │   ├── test_creditcard_blacklists.cpython-314-pytest-9.0.3.pyc
        │   ├── test_enterprises.cpython-314-pytest-9.0.2.pyc
        │   ├── test_enterprises.cpython-314-pytest-9.0.3.pyc
        │   ├── test_entitlements.cpython-314-pytest-9.0.2.pyc
        │   ├── test_entitlements.cpython-314-pytest-9.0.3.pyc
        │   ├── test_invoices.cpython-314-pytest-9.0.2.pyc
        │   ├── test_invoices.cpython-314-pytest-9.0.3.pyc
        │   ├── test_package_init.cpython-314-pytest-9.0.3.pyc
        │   ├── test_package_init.cpython-314.pyc
        │   ├── test_payment_methods.cpython-314-pytest-9.0.2.pyc
        │   ├── test_payment_methods.cpython-314-pytest-9.0.3.pyc
        │   ├── test_profile.cpython-314-pytest-9.0.2.pyc
        │   ├── test_profile.cpython-314-pytest-9.0.3.pyc
        │   ├── test_sendhub_error.cpython-314-pytest-9.0.2.pyc
        │   ├── test_sendhub_error.cpython-314-pytest-9.0.3.pyc
        │   ├── test_sendhub_object.cpython-314-pytest-9.0.2.pyc
        │   ├── test_sendhub_object.cpython-314-pytest-9.0.3.pyc
        │   ├── test_stripe_customers.cpython-314-pytest-9.0.2.pyc
        │   ├── test_stripe_customers.cpython-314-pytest-9.0.3.pyc
        │   ├── test_stripe_prices.cpython-314-pytest-9.0.2.pyc
        │   ├── test_stripe_prices.cpython-314-pytest-9.0.3.pyc
        │   ├── test_stripe_products.cpython-314-pytest-9.0.2.pyc
        │   ├── test_stripe_products.cpython-314-pytest-9.0.3.pyc
        │   ├── test_stripe_subscriptions.cpython-314-pytest-9.0.2.pyc
        │   ├── test_stripe_subscriptions.cpython-314-pytest-9.0.3.pyc
        │   ├── test_utils.cpython-314-pytest-9.0.2.pyc
        │   ├── test_utils.cpython-314-pytest-9.0.3.pyc
        │   ├── test_utils.cpython-314.pyc
        │   └── test_version.cpython-314-pytest-9.0.3.pyc
        ├── test_api_requestor.py
        ├── test_api_resource.py
        ├── test_billing_accounts.py
        ├── test_billing_plans.py
        ├── test_billing_prices.py
        ├── test_billing_products.py
        ├── test_constants.py
        ├── test_coupons.py
        ├── test_credit_notes.py
        ├── test_creditcard_blacklists.py
        ├── test_enterprises.py
        ├── test_entitlements.py
        ├── test_invoices.py
        ├── test_package_init.py
        ├── test_payment_methods.py
        ├── test_profile.py
        ├── test_sendhub_error.py
        ├── test_sendhub_object.py
        ├── test_stripe_customers.py
        ├── test_stripe_prices.py
        ├── test_stripe_products.py
        ├── test_stripe_subscriptions.py
        ├── test_utils.py
        └── test_version.py

6 directories, 130 files
```

- `sendhub/` – package source
- `sendhub/version.py` – dynamic version loader (reads `sendhub/VERSION`)
- `pyproject.toml` – modern build configuration replaces `setup.py`
- `MANIFEST.in` – ensures non-Python files (like VERSION) are in sdists

License
-----------------

This project is licensed under the terms of the [MIT License](LICENSE).

Contributing
-----------------

1. Fork the repo
2. Create a new branch: `git checkout -b feature/awesome`
3. Commit your changes: `git commit -m "Add awesome feature"`
4. Push and open a Pull Request
