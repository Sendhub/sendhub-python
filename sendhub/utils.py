import math as _math
import time as _time

from sendhub.constants import __UNDERSCORER2, _UNDERSCORER1


def camel_to_snake(_s):
    subbed = _UNDERSCORER1.sub(r'\1_\2', str(_s))
    return __UNDERSCORER2.sub(r'\1_\2', subbed).lower()


def convert_to_sendhub_object(resp):
    """Converts response object to send hub object"""
    from sendhub.entitlements import Entitlement
    from sendhub.sendhub_object import SendHubObject
    types = {'entitlement': Entitlement}

    if isinstance(resp, list):
        return [convert_to_sendhub_object(i) for i in resp]
    if isinstance(resp, dict):
        resp = resp.copy()
        klass_name = resp.get('object')
        if isinstance(klass_name, str):
            klass = types.get(klass_name, SendHubObject)
        else:
            klass = SendHubObject
        return klass.construct_from(resp)
    return resp


def retry(tries, delay=3, backoff=2, desired_outcome=True, _fail_value=None):
    """
    Retry decorator with exponential backoff
    Retries a function or method until it produces a desired outcome.

    Args:
        tries (int): no of try
        delay (int): Sets the initial delay in seconds, and backoff sets the factor by which the delay should lengthen after each failure.
        backoff (int): Must be greater than 1, or else it isn't really a backoff.  Tries must be at least 0, and delay greater than 0.
        desired_outcome (value / callable): Can be a value or a callable. If it is a callable the produced value will be passed and success is presumed if the invocation returns True.
        _fail_value: Value to return in the case of failure.

    """

    if backoff <= 1:
        raise ValueError('backoff must be greater than 1')

    tries = _math.floor(tries)
    if tries < 0:
        raise ValueError('tries must be 0 or greater')

    if delay <= 0:
        raise ValueError('delay must be greater than 0')

    def wrapped_retry(_fn):
        """Decorative wrapper."""

        def retry_fn(*args, **kwargs):
            """The function which does the actual retrying."""
            # Make mutable:
            mtries, mdelay = tries, delay

            # First attempt.
            _rv = _fn(*args, **kwargs)

            while mtries > 0:
                if (_rv == desired_outcome or (callable(desired_outcome) and desired_outcome(_rv) is True)):
                    # Success.
                    return _rv

                # Consume an attempt.
                mtries -= 1

                # Wait...
                _time.sleep(mdelay)

                # Make future wait longer.
                mdelay *= backoff

                # Try again.
                _rv = _fn(*args, **kwargs)

            # Ran out of tries :-(
            return False

        # True decorator -> decorated function.
        return retry_fn

    # @retry(arg[, ...]) -> decorator.
    return wrapped_retry




