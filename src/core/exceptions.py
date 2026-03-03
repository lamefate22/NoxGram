class CryptoError(Exception):
    """The exception is related to the operation of encryption."""
    __slots__ = ()
    def __init__(self, message: str = "An unexpected error occurred in the module."):
        super().__init__(message)

class ConfigError(Exception):
    """The exception is related to config operations."""
    __slots__ = ()
    def __init__(self, message: str = "An unexpected error occurred in the module."):
        super().__init__(message)

class AuthError(Exception):
    """The exception is related to authentication."""
    __slots__ = ()
    def __init__(self, message: str = "An unexpected error occurred in the module."):
        super().__init__(message)
