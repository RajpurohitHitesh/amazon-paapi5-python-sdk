# Sample content of exceptions.py to illustrate the structure

class AmazonAPIException(Exception):
    def __init__(self, message, error_code=None, status_code=None):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class SomeSpecificException(AmazonAPIException):
    def __init__(self, message, error_code=None, status_code=None):
        super().__init__(message, error_code, status_code)


class AnotherException(AmazonAPIException):
    def __init__(self, message, error_code=None, status_code=None):
        super().__init__(message, error_code, status_code)
