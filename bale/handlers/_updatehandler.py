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

import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, cast

from .._utils.checkers import iscoroutinefunction

if TYPE_CHECKING:
    from bale.context import Context
    from bale.handlers import Cooldown

__all__ = ("UpdateHandler",)

CoroT: TypeAlias = Callable[..., Coroutine[Any, Any, Any]]
ErrorCallbackT = TypeVar("ErrorCallbackT", bound=CoroT)


class UpdateHandler:
    """This object shows a Update Handler.
    All handlers are subclasses of this handler. In this handler, updates are only covered.

    This is a base class for all update handlers. You can create custom handlers by inheriting from it.

    Note:
        Follow the steps below to create a custom handler:

        1. Create a subclass of :class:`~bale.handlers.UpdateHandler`.

        .. code-block:: python

            from bale.handlers import UpdateHandler

            class MyHandler(UpdateHandler):
                pass

        2. Create the method :meth:`check_new_update` inside the class when processing updates, the :meth:`check_new_update` method is called. This method must return either :obj:`None` or a :obj:`tuple`.

        .. code-block:: python

            from bale.handlers import UpdateHandler

            class MyHandler(UpdateHandler):
                def check_new_update(self, context: "Context") -> tuple["Message"] | None:
                    update = ctx.update
                    target_message = update.message or update.edited_message
                    if target_message:
                        return (
                            target_message,
                        )

                    return None

        3. Now, use customized handler!

        .. code-block:: python

            ...
            bot = bale.Bot(token="YOUR_TOKEN_HERE")

            @bot.handle(MyHandler())
            async def my_custom_handler(message: Message) -> Message:
                return await message.reply("Hello World!")

    .. admonition:: Input parameters for the wrapper function
        :class: seealso

        **context**: :class:`~bale.context.Context`
            The only parameter for this handler is the received context object.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.handlers import UpdateHandler
                from bale.context import Context

                @client.handle(UpdateHandler())
                async def update_handler(context: Context):
                    return await message.reply(f'new update {ctx.update.update_id}')

    .. versionadded:: 3.0
    """

    __slots__ = ("kwargs_handler", "_callback", "_on_error", "_self")

    def __init__(self, **kwargs) -> None:
        self.kwargs_handler = kwargs
        self._callback: CoroT | None = None
        self._on_error: Callable[["Context", Exception], Coroutine] | None = None
        self._self: Any = None

    @property
    def callback(self) -> CoroT | None:
        """Wrapper function configured for the handler.

        .. note ::
            To set up the wrapper function, you can use either the :meth:`set_callback` method or the code snippet below:

            .. code-block:: python

                async def message_handler_callback(message: Message):
                    return await message.reply("Hello World!")

                handler.callback = message_handler_callback

        See Also:
            :meth:`set_callback`
        """
        return self._callback

    @callback.setter
    def callback(self, func: CoroT) -> None:
        self.set_callback(func)

    async def _on_error_wrapper(self, context: "Context", exc: Exception):
        try:
            context.bot.dispatch("handler_error", self, context, exc)
        except asyncio.CancelledError:
            pass

        if self._on_error:
            args: tuple[Any, ...] = (
                (context, exc) if not self._self else (self._self, context, exc)
            )

            await self._on_error(*args)

    def set_callback(self, callback: CoroT) -> None:
        """Register new handler callback.

        Each handler provides its specific parameters to its covering function. Therefore, each callback function must have different parameters depending on its handler.

        Important:
            Wrapper functions should follow the format below:

            .. code-block:: python

                async def custom_handler_callback(parameter1, parameter2, ...):
                    pass

        Arguments:
            callback:
                The new callback function.
        """
        if not iscoroutinefunction(callback):
            raise TypeError(
                f"Callback of {self!r} expected a coroutine function not {type(callback).__name__!r}"
            )

        self._callback = callback

    async def check_new_update(self, context: "Context") -> tuple[Any] | None:
        """This function determines whether the "update" should be covered by the handler or not.

        Arguments:
            context:
                The context to be tested.

        See Also:
            :meth:`handle_update`

        Returns:
             If :obj:`False` or :obj:`None` is returned, the update should not be wrapped by the handler, otherwise the handler is required to wrap that update.
        """
        return (context,)

    def error(self, func: ErrorCallbackT) -> ErrorCallbackT:
        """
        A decorator to set the ``on_error`` function for a handler.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale import Update, Message
                from bale.handlers import MessageHandler

                ...

                @bot.handle(MessageHandler())
                async def message_handler(message: Message):
                    return await message.reply("Hello World!")

                @message_handler.error
                async def message_handler_error(update: Update, exc: Exception):
                    if not update.message:
                        return
                    return await update.message.reply("The handler encountered an error")

        """
        self.set_error_callback(func)
        return func

    def set_error_callback(self, func) -> None:
        if not iscoroutinefunction(func):
            raise TypeError(
                f"error for {self!r} expected a coroutine function not {type(func).__name__!r}"
            )

        self._on_error = func

    async def _run_callback(self, context: "Context", *args) -> Any:
        callback = self.callback
        if callback is None:
            return None

        if cooldown_obj := getattr(callback, "__cooldown__", None):
            cast("Cooldown", cooldown_obj).update_rate_limit(context)

        if self._self:
            args = (self._self,) + args

        return await callback(*args)

    async def handle_update(self, context: "Context", *args):
        """This function works if the handler is required to cover the new Update and calls the :attr:`callback`
        function.

        TODO: CHANGE DOCS

        Arguments:
            context:
                The update to be tested.
            args:
                Additional objects, if given to this parameter, will be passed directly to the :attr:`callback`
                function.

        See Also:
            :meth:`check_new_update`
        """
        if self.callback:
            try:
                return await self._run_callback(context, *args)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                return await self._on_error_wrapper(context, exc)

        return None

    def __repr__(self) -> str:
        callback_n = getattr(self._callback, "__qualname__", None) or getattr(
            self._callback,
            "__name__",
            (repr(self._callback) if self._callback else "None"),
        )
        parts = [f"callback={callback_n}"]

        if self.kwargs_handler:
            kwargs_repr = ", ".join(
                f"{k}={v!r}" for k, v in self.kwargs_handler.items()
            )
            parts.append(kwargs_repr)

        return f"<{self.__class__.__name__}({', '.join(parts)})>"
