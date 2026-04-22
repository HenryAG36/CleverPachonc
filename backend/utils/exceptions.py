class CleverPachoncError(Exception):
    pass


class APIError(CleverPachoncError):
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(APIError):
    pass


class NotFoundError(APIError):
    pass


class AuthError(APIError):
    pass


class NetworkError(CleverPachoncError):
    pass


class ConfigError(CleverPachoncError):
    pass
