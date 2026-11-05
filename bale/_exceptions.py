# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context import Context
    from .handlers import Cooldown
    from .middleware import BaseMiddleware

__all__ = (
    "BaleError",
    "InvalidToken",
    "RateLimited",
    "NetworkError",
    "TimeOut",
    "NotFound",
    "Forbidden",
    "BadRequest",
    "MiddlewareError",
    "HandlerError",
    "HandlerOnCooldown",
    "CommandHandlerError",
    "UserInputError",
    "MissingRequiredArgument",
    "BadArgument",
    "ConversationFlowError",
    "FlowBadStatusError",
    "FlowBadProtocolError",
    "FlowTimeoutError",
    "FlowStateCorruptedError",
)


class BaleError(Exception):
    """Base exception class for all errors in ``python-bale-bot``.

    Attributes:
        message (:obj:`~typing.Any`): The text of the error. Could be :obj:`None`.
    """

    __slots__ = ("message",)

    def __init__(self, message: Any) -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self):
        """:meta private:"""
        return f"{self.__class__.__name__}: {self.message}"

    def __reduce__(self):
        """:meta private:"""
        return self.__class__, (self.message,)


class InvalidToken(BaleError):
    """Exception raised when the provided token is invalid or the Bale bot service reports that the token is not found."""

    __slots__ = ("_message",)

    def __init__(self, message=None) -> None:
        message = (message or "The token is invalid.") + (
            "\nYou must obtain the bot token from `@BotFather` (https://ble.ir/BotFather) and then place it in the `token` parameter."
        )
        super().__init__(message)

    @staticmethod
    def check_description(description: str | None) -> bool:
        """Check whether the server response description indicates a missing or invalid token.

        Args:
            description (:obj:`str` | :obj:`None`): The error description from the API response.

        Returns:
            :obj:`True` if the description indicates the token was not found, :obj:`False` otherwise.
        """
        return bool(description and "token not found" in description.lower())


class NetworkError(BaleError):
    """Exception raised when connection is closed due to network errors that could not be handled or resolved internally."""

    __slots__ = ()


class TimeOut(BaleError):
    """Exception raised when a request sent to the server times out."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Timed Out")


class NotFound(BaleError):
    """Exception raised when a requested resource is not found on the Bale server (HTTP status code 404)."""

    __slots__ = ()

    def __init__(self, message: Any = None) -> None:
        super().__init__(message or "Not Found")


class Forbidden(BaleError):
    """Exception raised when access to a resource is forbidden (HTTP status code 403)."""

    __slots__ = ()


class BadRequest(BaleError):
    """Exception raised when the Bale server returns a Bad Request error (HTTP status code 400)."""

    __slots__ = ()


class MiddlewareError(BaleError):
    """Exception raised when an error is thrown during middleware execution.

    Attributes:
        middleware (:class:`~bale.middleware.BaseMiddleware`): The associated middleware instance where the error occurred.

    .. versionadded:: 3.0
    """

    __slots__ = ("middleware",)

    def __init__(self, middleware: "BaseMiddleware", exc: Any) -> None:
        super().__init__(exc)
        self.middleware = middleware


class RateLimited(BaleError):
    """Exception raised when API request rate reaches the limit.

    Attributes:
        retry_after (:obj:`float` | :obj:`int` | :obj:`None`): The retry after duration in seconds, if available.
    """

    __slots__ = ("retry_after",)

    def __init__(self, retry_after: float | int | None = None) -> None:
        message = "We are Rate Limited"
        if retry_after:
            message += f": retry after={retry_after}"
        super().__init__(message)
        self.retry_after = retry_after


class HandlerError(BaleError):
    """Base exception class for all errors related to handler execution and management.

    .. versionadded:: 3.0
    """

    __slots__ = ()


class HandlerOnCooldown(BaleError):
    """Exception raised when a handler is on cooldown and not permitted to be invoked again yet.

    Attributes:
        cooldown (:class:`~bale.handlers.Cooldown`): The cooldown instance associated with the handler.
        context (:class:`~bale.context.Context`): The invocation context.
        retry_after (:obj:`float` | :obj:`int`): The number of seconds remaining until the cooldown expires.

    .. versionadded:: 3.0
    """

    __slots__ = ("cooldown", "context", "retry_after")

    def __init__(
        self, cooldown: "Cooldown", context: "Context", retry_after: float | int
    ) -> None:
        super().__init__(
            f"Handler is on cooldown. Please try again in {retry_after:.2f} seconds."
        )
        self.cooldown = cooldown
        self.context = context
        self.retry_after = retry_after


class CommandHandlerError(HandlerError):
    """Base exception class for errors related to command handler processing and execution.

    .. versionadded:: 3.0
    """

    __slots__ = ()


class UserInputError(CommandHandlerError):
    """Exception raised when an error is caused by invalid or incomplete user input while issuing a command.

    .. versionadded:: 3.0
    """

    __slots__ = ()


class MissingRequiredArgument(UserInputError):
    """Exception raised when one of the mandatory arguments defined for a command is not provided by the user.

    Attributes:
        parameter (:obj:`str`): The name of the missing required parameter.

    .. versionadded:: 3.0
    """

    __slots__ = ("parameter",)

    def __init__(self, parameter_name: str) -> None:
        self.parameter = parameter_name
        super().__init__(f"The required parameter '{parameter_name}' is missing.")


class BadArgument(UserInputError):
    """Exception raised when a command argument provided by the user cannot be converted to the expected type.

    Attributes:
        parameter (:obj:`str`): The name of the parameter.
        raw_input (:obj:`str`): The raw input value supplied by the user.
        expected_type (:obj:`~typing.Any`): The expected target type.

    .. versionadded:: 3.0
    """

    __slots__ = ("parameter", "raw_input", "expected_type")

    def __init__(self, parameter_name: str, raw_input: str, expected_type) -> None:
        self.parameter = parameter_name
        self.raw_input = raw_input
        self.expected_type = expected_type
        super().__init__(
            f"Could not convert argument '{parameter_name}'"
            f" with value {raw_input!r} to type '{expected_type}'."
        )


class ConversationFlowError(BaleError):
    """Base exception class for errors originating from the conversation flow subsystem.

    .. versionadded:: 3.0
    """

    __slots__ = ()


class FlowBadStatusError(ConversationFlowError):
    """Exception raised when the conversation flow status is invalid.

    Attributes:
        status (:obj:`~typing.Any`): The invalid flow status encountered.

    .. versionadded:: 3.0
    """

    __slots__ = ("status",)

    def __init__(self, status: Any) -> None:
        super().__init__(f"Bad flow status: {status!r}")
        self.status = status


class FlowBadProtocolError(ConversationFlowError):
    """Exception raised when the returned conversation flow protocol is invalid.

    Attributes:
        protocol (:obj:`~typing.Any`): The invalid transition protocol received.

    .. versionadded:: 3.0
    """

    __slots__ = ()

    def __init__(self, protocol, message: str = "Bad transition protocol") -> None:
        super().__init__(f"{message}: {protocol!r}")
        self.protocol = protocol


class FlowTimeoutError(ConversationFlowError):
    """Exception raised when a conversation expires due to failing to start the next step within the designated time interval."""

    __slots__ = ()


class FlowStateCorruptedError(ConversationFlowError):
    """Exception raised when the conversation flow state in storage is corrupted, incomplete, or belongs to another conversation flow.

    .. versionadded:: 3.0
    """

    __slots__ = ()
