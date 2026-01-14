import logging
import os
import re
from typing import Optional

HTTP_LIB: str = "requests"
LOGGER: logging.Logger = logging.getLogger("sendhub")

# Environment detail for logging control
ENVIRONMENT_DETAIL: str = os.getenv("ENVIRONMENT_DETAIL", "development")

# Set logger level ONCE based on environment
if ENVIRONMENT_DETAIL == "production":
    LOGGER.setLevel(logging.ERROR)
else:
    LOGGER.setLevel(logging.DEBUG)

# Remove all handlers if already set (avoid duplicate logs in some environments)
if LOGGER.hasHandlers():
    LOGGER.handlers.clear()

# Add a simple console handler
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)

# Configuration variables
USERNAME: Optional[str] = None
PASSWORD: Optional[str] = None
INTERNAL_API: bool = False
API_BASE: str = "https://api.sendhub.com"
ENTITLEMENTS_BASE: str = "https://entitlements.sendhub.com"
PROFILE_BASE: str = "https://profile.sendhub.com"
BILLING_BASE: str = "https://billing.sendhub.com"
API_VERSION: Optional[str] = None

_UNDERSCORER1 = re.compile(r"(.)([A-Z][a-z]+)")
__UNDERSCORER2 = re.compile(r"([a-z0-9])([A-Z])")

"""
Constants and configuration for SendHub API client.

This module sets up logging, environment-based configuration, and provides
base URLs and global variables for API usage.
"""
