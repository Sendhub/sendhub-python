sendhub-python
=========

SendHub Python bindings for [SendHub](https://sendhub.com/).

Table Of Contents
-----------------

- [sendhub-python](#sendhub-python)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [What's New](#whats-new)
    - [Version 0.26.01 (Latest)](#version-02601-latest)
    - [Python Packaging Enhancements](#python-packaging-enhancements)
    - [Enhanced Authentication Session Management](#enhanced-authentication-session-management)
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

### Version 0.26.01 (Latest)

### Python Packaging Enhancements

- `pyproject.toml`: Earlier settings.py was being used to build the package from repo, now pyproject.toml will be used.

### Enhanced Authentication Session Management

- **Support for Python 3.13**: Keeping the implemented logic same, the code has been improved to utilize python 3.13
- **New endpoints under Billing Accounts**: To accomodate the stripe changes the billing account has been enhanced.

> **Migration Note**: This release maintains full backward compatibility. No breaking changes were introduced.

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

```txt
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── pytest-report.xml
├── README.md
├── sendhub
│   ├── __init__.py
│   ├── api_requestor.py
│   ├── api_resource.py
│   ├── billing_accounts.py
│   ├── billing_plans.py
│   ├── billing_prices.py
│   ├── billing_products.py
│   ├── constants.py
│   ├── creditcard_blacklists.py
│   ├── enterprises.py
│   ├── entitlements.py
│   ├── profile.py
│   ├── sendhub_error.py
│   ├── sendhub_object.py
│   ├── utils.py
│   ├── VERSION
│   └── version.py
└── tests
    └── unit
        ├── test_api_requestor.py
        ├── test_api_resource.py
        ├── test_billing_accounts.py
        ├── test_billing_plans.py
        ├── test_billing_prices.py
        ├── test_billing_products.py
        ├── test_creditcard_blacklists.py
        ├── test_enterprises.py
        ├── test_entitlements.py
        ├── test_profile.py
        ├── test_sendhub_error.py
        ├── test_sendhub_object.py
        └── test_utils.py
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
