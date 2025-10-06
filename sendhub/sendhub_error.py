# Exceptions
class SendHubError(Exception):
    """Custom Exception for SendHub"""
    def __init__(self, message=None, dev_message=None, code=None, more_info=None):
        super().__init__(message)
        self.dev_message = dev_message if dev_message is not None else ''
        self.code = code if code is not None else -1
        self.more_info = more_info if more_info is not None else ''


class APIError(SendHubError):
    """Exception class for API Error"""
    pass


class APIConnectionError(SendHubError):
    """Exception class for API Connection Error"""
    pass


class EntitlementError(SendHubError):
    """Exception class for Entitlement Error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class InvalidRequestError(SendHubError):
    """Exception class for Invalid Request Error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class TryAgainLaterError(SendHubError):
    """Exception class for Try AgainLater error"""
    def __init__(self, message, dev_message=None, code=None, more_info=None):
        super().__init__(message, dev_message, code, more_info)


class AuthenticationError(SendHubError):
    """Exception class for Authentication Error"""
    pass


class AuthorizationError(SendHubError):
    """Exception class for Authorization Error"""
    pass
