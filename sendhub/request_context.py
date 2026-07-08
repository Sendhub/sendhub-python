"""
Per-request context propagated onto outbound SendHub API calls.

Every sister service (inforeach, billing, admin, entitlements, profile, voice,
inboundsms) already assigns a request id to each inbound request by reading an
``X-Request-ID`` header and falling back to a fresh UUID only when it's absent.
That means tagging an outbound call made *during* handling of an inbound
request with the inbound request's id is enough for the receiving service to
adopt it as its own, tying the whole call chain together under one id with no
changes needed on the receiving side.

Call ``set_current_request_id`` when a request starts (mirroring each
service's own ``set_request_id`` call into its local logging context) and
clear it when the request ends. ``APIRequestor.perform_request`` reads it via
``get_current_request_id`` and attaches it as the ``X-Request-ID`` header on
every outbound call.
"""

import contextvars

_request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "sendhub_current_request_id", default=None
)


def set_current_request_id(request_id: str | None) -> contextvars.Token:
    """Bind the current request id for the active thread/async task."""
    return _request_id_ctx.set(request_id)


def reset_current_request_id(token: contextvars.Token) -> None:
    """Undo a prior set_current_request_id() call using its returned token."""
    _request_id_ctx.reset(token)


def get_current_request_id() -> str | None:
    """Return the request id bound for the active thread/async task, if any."""
    return _request_id_ctx.get()
