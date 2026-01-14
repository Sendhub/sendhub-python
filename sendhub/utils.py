import time as _time
from typing import Any, Callable, Optional, TypeVar, Union

from sendhub.constants import __UNDERSCORER2, _UNDERSCORER1


def camel_to_snake(_s: str) -> str:
    if not isinstance(_s, str):
        raise TypeError(f"Input to camel_to_snake must be str, got {type(_s).__name__}")
    subbed = _UNDERSCORER1.sub(r"\1_\2", _s)
    return __UNDERSCORER2.sub(r"\1_\2", subbed).lower()


def convert_to_sendhub_object(resp: Any) -> Any:
    """Converts response object to send hub object"""
    from sendhub.entitlements import Entitlement
    from sendhub.sendhub_object import SendHubObject

    types = {"entitlement": Entitlement}

    if isinstance(resp, list):
        return [convert_to_sendhub_object(i) for i in resp]
    if isinstance(resp, dict):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, str):
            klass = types.get(klass_name, SendHubObject)
        else:
            klass = SendHubObject
        return klass.construct_from(resp)
    return resp


T = TypeVar("T")


def retry(
    tries: int,
    delay: int = 3,
    backoff: int = 2,
    desired_outcome: Union[Any, Callable[[Any], bool]] = True,
    _fail_value: Optional[Any] = None,
) -> Callable[[Callable[..., T]], Callable[..., Union[T, bool]]]:
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

    import logging

    LOGGER = logging.getLogger("sendhub")

    if not isinstance(tries, int) or tries < 0:
        raise ValueError("tries must be an integer >= 0")
    if not isinstance(delay, int) or delay <= 0:
        raise ValueError("delay must be an integer > 0")
    if not isinstance(backoff, int) or backoff <= 1:
        raise ValueError("backoff must be an integer > 1")


    def wrapped_retry(_fn: Callable[..., T]) -> Callable[..., Union[T, bool]]:
        """Decorative wrapper."""

        def retry_fn(*args, **kwargs) -> Union[T, bool]:
            mtries, mdelay = tries, delay
            attempt = 1

            LOGGER.debug(f"Retry: Attempt {attempt} of {tries+1}")
            _rv = _fn(*args, **kwargs)

            while mtries > 0:
                if callable(desired_outcome):
                    if desired_outcome(_rv):
                        LOGGER.debug(f"Retry: Success on attempt {attempt}")
                        return _rv
                elif _rv == desired_outcome:
                    LOGGER.debug(f"Retry: Success on attempt {attempt}")
                    return _rv

                mtries -= 1
                LOGGER.debug(
                    f"Retry: Failure on attempt {attempt}, {mtries} tries left. Waiting {mdelay} seconds before next attempt."
                )
                _time.sleep(mdelay)
                mdelay *= backoff
                attempt += 1
                _rv = _fn(*args, **kwargs)

            LOGGER.debug(f"Retry: All {tries+1} attempts failed.")
            return _rv if callable(desired_outcome) else False

        return retry_fn

    return wrapped_retry
