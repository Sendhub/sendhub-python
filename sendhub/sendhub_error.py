

class SendHubError(Exception):
    """
    Base exception for SendHub errors.

    Attributes:
        message (str): Human-readable error message.
        dev_message (str): Developer-focused error message.
        code (int): Error code.
        more_info (str): Additional information.
    """

    def __init__(
        self,
        message: str | None = None,
        dev_message: str | None = None,
        code: int | None = None,
        more_info: str | None = None,
    ) -> None:
        super().__init__(message)
        self.dev_message: str = dev_message if dev_message is not None else ""
        self.code: int = code if code is not None else -1
        self.more_info: str = more_info if more_info is not None else ""


class APIError(SendHubError):
    """Exception for API errors."""

    pass


class APIConnectionError(SendHubError):
    """Exception for API connection errors."""

    pass


class EntitlementError(SendHubError):
    """Exception for entitlement errors."""

    def __init__(
        self,
        message: str,
        dev_message: str | None = None,
        code: int | None = None,
        more_info: str | None = None,
    ) -> None:
        super().__init__(message, dev_message, code, more_info)


class InvalidRequestError(SendHubError):
    """Exception for invalid request errors."""

    def __init__(
        self,
        message: str,
        dev_message: str | None = None,
        code: int | None = None,
        more_info: str | None = None,
    ) -> None:
        super().__init__(message, dev_message, code, more_info)


class TryAgainLaterError(SendHubError):
    """Exception for 'try again later' errors."""

    def __init__(
        self,
        message: str,
        dev_message: str | None = None,
        code: int | None = None,
        more_info: str | None = None,
    ) -> None:
        super().__init__(message, dev_message, code, more_info)


class AuthenticationError(SendHubError):
    """Exception for authentication errors."""

    pass


class AuthorizationError(SendHubError):
    """Exception for authorization errors."""

    pass
