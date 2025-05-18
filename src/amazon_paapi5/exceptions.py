class AmazonAPIException(Exception):
    """Base exception for Amazon PA-API errors."""
    pass

class AuthenticationException(AmazonAPIException):
    """Raised when authentication fails (e.g., invalid credentials)."""
    def __init__(self, message="Authentication failed. Check your access key, secret key, or encryption key."):
        super().__init__(message)

class ThrottleException(AmazonAPIException):
    """Raised when the API rate limit is exceeded."""
    def __init__(self, message="Rate limit exceeded. Try increasing throttle_delay or retrying later."):
        super().__init__(message)

class InvalidParameterException(AmazonAPIException):
    """Raised when invalid parameters are provided."""
    def __init__(self, message="Invalid request parameters provided."):
        super().__init__(message)

class ResourceValidationException(AmazonAPIException):
    """Raised when invalid resources are specified."""
    def __init__(self, message="Invalid resources specified for the operation."):
        super().__init__(message)