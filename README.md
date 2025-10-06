
sendhub-python
=========

SendHub Python bindings for [SendHub](https://sendhub.com/).

Table Of Contents
-----------------

- [sendhub-python](#sendhub-python)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [What's New](#whats-new)
    - [Version 0.25.10 (Latest)](#version-02510-latest)
    - [Python Packaging Enhancements](#python-packaging-enhancements)
    - [Enhanced Authentication Session Management](#enhanced-authentication-session-management)
  - [Installation](#installation)
  - [Building \& Packaging](#building--packaging)
  - [Testing The Build](#testing-the-build)
  - [Development Workflow](#development-workflow)
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

### Version 0.25.10 (Latest)

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

Project Layout
-----------------

```txt
.
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── sendhub
│   ├── __init__.py
│   ├── __pycache__
│   ├── VERSION
│   └── version.py
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
