import logging
import re

HTTP_LIB = 'requests'
LOGGER = logging.getLogger('sendhub')

# Configuration variables
USERNAME = None
PASSWORD = None
INTERNAL_API = False
API_BASE = 'https://api.sendhub.com'
ENTITLEMENTS_BASE = 'https://entitlements.sendhub.com'
PROFILE_BASE = 'https://profile.sendhub.com'
BILLING_BASE = 'https://billing.sendhub.com'
API_VERSION = None

_UNDERSCORER1 = re.compile(r'(.)([A-Z][a-z]+)')
__UNDERSCORER2 = re.compile('([a-z0-9])([A-Z])')
