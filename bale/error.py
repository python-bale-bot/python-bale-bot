"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations
from typing import Optional
class HTTPClientError:
    USER_OR_CHAT_NOT_FOUND = "no such group or user"
    TOKEN_NOT_FOUND = "Bad Request: Token not found"
    RATE_LIMIT = "bot limit exceed"
    LOCAL_RATE_LIMIT = "local_rate_limited"
    PERMISSION_DENIED = "permission_denied"

class BaleError(Exception):
    """
    Base exception class for python-bale-bot

    Attributes
    ------------
    message: :class:`str`
        The text of the error. Could be an `None`.
    """
    __slots__ = (
        "message",
    )

    @staticmethod
    def check_response(description: Optional[str]) -> bool:
        return False

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
    """
    An exception where the server says the Token is Invalid
    """
    __slots__ = ("_message",)

    def __init__(self, message=None):
        super().__init__(message or "Invalid Token")

    @staticmethod
    def check_response(description: Optional[str]) -> bool:
        return description and "token not found" in description.lower()

class APIError(BaleError):
    """
    Exception that's raised for when status code 400 occurs and Error is Unknown.
    Subclass of :exc:`BaleError`
    """
    __slots__ = ()

    def __init__(self, error_code, message):
        super().__init__("{}: {}".format(error_code, message))


class NetworkError(BaleError):
    """
    Exception that's raised when the connection is
    closed for reasons that could not be handled internally.
    """
    __slots__ = ()


class TimeOut(BaleError):
    __slots__ = ()

    def __init__(self):
        super().__init__("Time Out")


class NotFound(BaleError):
    """
    Exception that's raised for when status code 404 occurs.
    Subclass of :exc:`BaleError`
    """
    __slots__ = ()

    def __init__(self, message=None):
        super().__init__(message or "Not Found")

    @staticmethod
    def check_response(description: Optional[str]) -> bool:
        return description and HTTPClientError.USER_OR_CHAT_NOT_FOUND in description

class Forbidden(BaleError):
    """
    Exception that's raised for when status code 403 occurs.
    Subclass of :exc:`BaleError`
    """
    __slots__ = ()

    def __init__(self, message=None):
        super().__init__(message or "Forbidden")

    @staticmethod
    def check_response(description: Optional[str]) -> bool:
        return description and description.startswith("Forbidden:")

class BadRequest(BaleError):
    """
    Exception that's raised for when Bale server say Bad Request.
    Subclass of :exc:`BaleError`
    """
    __slots__ = ()

    def __init__(self, error):
        super().__init__(error)

    @staticmethod
    def check_response(description: Optional[str]) -> bool:
        return description and description.startswith("Bad Request:")

class RateLimited(BaleError):
    """
    Exception that's raised for when Rate Limits.
    Subclass of :exc:`BaleError`
    """
    __slots__ = ()

    def __init__(self):
        super().__init__("We are Rate Limited")

class HTTPException(BaleError):
    """
    Exception that's raised when an HTTP request operation fails.
    """
    __slots__ = ()

    def __init__(self, error):
        super().__init__(str(error))
