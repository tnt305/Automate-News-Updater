class BaseError(Exception):
    """
    Base class for all errors in this package.
    """
    def __init__(self, message = 'An error occurred'):
        super().__init__(message)
        self.message = message