class AmazonAPIException(Exception):
    """Base exception for Amazon PA-API errors."""
    def __init__(self, message: str, response_errors: list = None):
        super().__init__(message)
        self.response_errors = response_errors or []

    def get_response_errors(self) -> list:
        """Get list of specific API error responses."""
        return self.response_errors

class AuthenticationException(AmazonAPIException):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed. Check your credentials.", response_errors=None):
        super().__init__(message, response_errors)

class ThrottleException(AmazonAPIException):
    """Raised when the API rate limit is exceeded."""
    def __init__(self, message="Rate limit exceeded. Try increasing throttle_delay.", response_errors=None):
        super().__init__(message, response_errors)
        self.retry_after = None  # Can be set when server provides retry-after header

    def set_retry_after(self, seconds: int) -> None:
        """Set the recommended retry delay."""
        self.retry_after = seconds

class InvalidParameterException(AmazonAPIException):
    """Raised when invalid parameters are provided."""
    def __init__(self, message="Invalid request parameters provided.", response_errors=None, invalid_params=None):
        super().__init__(message, response_errors)
        self.invalid_params = invalid_params or []

class ResourceValidationException(AmazonAPIException):
    """Raised when invalid resources are specified."""
    def __init__(self, message="Invalid resources specified for the operation.", response_errors=None, invalid_resources=None):
        super().__init__(message, response_errors)
        self.invalid_resources = invalid_resources or []

class ConfigException(AmazonAPIException):
    """Raised when configuration is invalid."""
    def __init__(self, message="Invalid configuration provided.", missing_fields=None):
        super().__init__(message)
        self.missing_fields = missing_fields or []

class SecurityException(AmazonAPIException):
    """Raised for security-related issues."""
    def __init__(self, message="Security error occurred.", error_type=None):
        super().__init__(message)
        self.error_type = error_type

class NetworkException(AmazonAPIException):
    """Raised for network-related issues."""
    def __init__(self, message="Network error occurred.", original_error=None):
        super().__init__(message)
        self.original_error = original_error

class CacheException(AmazonAPIException):
    """Raised for caching-related issues."""
    def __init__(self, message="Cache operation failed.", cache_operation=None):
        super().__init__(message)
        self.cache_operation = cache_operation