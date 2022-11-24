class HTTPClientError:
    USER_OR_CHAT_NOT_FOUND = "no such group or user"
    RATE_LIMIT = "bot limit exceed"
    LOCAL_RATE_LIMIT = "local_rate_limited"
    PERMISSION_DENIED = "permission_denied"

class BaleError(Exception):
    __slots__ = (
        "message",
    )

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}\n('{self.message}')"

    def __reduce__(self):
        return self.__class__, (self.message,)


class InvalidToken(BaleError):
    __slots__ = ("_message",)

    def __init__(self, message):
        self._message = message

        super().__init__("Invalid Token" if self._message is not None else self._message)


class APIError(BaleError):
    __slots__ = ()

    def __init__(self, error_code, message):
        super().__init__("{}: {}".format(error_code, message))


class NetworkError(BaleError):
    __slots__ = ()


class TimeOut(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("Time Out")


class NotFound(BaleError):
    __slots__ = ()

    def __init__(self, message=None):
        super().__init__(message if message else "Not Found")


class Forbidden(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("Forbidden")

class RateLimited(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("We are Rate Limited")

class HTTPException(BaleError):
    __slots__ = ()

    def __init__(self, response):
        super().__init__(str(response))
