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
        return f"{self.__class__.__name__}('{self.message}')"

    def __reduce__(self):
        return self.__class__, (self.message,)


class InvalidToken(BaleError):
    __slots__ = ("_message",)

    def __init__(self, message):
        self._message = message

        super().__init__("Invalid Token" if self._message is not None else self._message)


class NetworkError(BaleError):
    __slots__ = ()


class TimeOut(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("Time Out")
