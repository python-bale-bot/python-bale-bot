# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import Coroutine, Callable, Tuple, Optional, TYPE_CHECKING, TypeVar
import asyncio
from bale.utils.types import UT

if TYPE_CHECKING:
    from bale import Update

__all__ = (
    "BaseHandler",
)

ER = TypeVar("ER")

class BaseHandler:
    """This object shows a Base Handler.
    This is a base class for all update handlers. You can create custom handlers by inheriting from it.

    .. important::
        Follow the steps below to create a custom handler:
        1. Create a subclass of :class:`bale.BaseHandler`.

            .. code:: python

                from bale.handlers import BaseHandler

                class MyHandler(BaseHandler):
                    pass

        2. Create the method :meth:`check_new_update` inside the class
        When processing updates, the :meth:`check_new_update` method is called. This method must return either None or a tuple.

            .. code:: python

                from bale.handlers import BaseHandler

                class MyHandler(BaseHandler):
                    def check_new_update(self, update: "Update") -> Optional[Tuple["Message"]]:
                        target_message = update.message or update.edited_message
                        if target_message:
                            return (
                                target_message,
                            )

                        return None

        3. Now, use that customized handler!

            .. code:: python

                ...
                bot = bale.Bot(token="YOUR_TOKEN_HERE")

                @bot.handle(MyHandler())
                async def my_custom_handler(message: Message) -> Message:
                    return await message.reply("Hello World!")

    """
    __slots__ = (
        "_callback",
        "_on_error"
    )

    def __init__(self) -> None:
        self._callback: Optional[Callable[[UT], Coroutine[...]]] = None
        self._on_error: Optional[Callable[[Update, Exception], Coroutine]] = None

    @property
    def callback(self) -> Optional[Callable[[UT], Coroutine[...]]]:
        return self._callback

    @callback.setter
    def callback(self, _):
        raise ValueError(
            "You can't set callback because it's not an public attribute"
        )

    async def _on_error_wrapper(self, update: Update, exc: Exception):
        try:
            update.get_bot().dispatch('handler_error', self, update, exc)
        except asyncio.CancelledError:
            pass

        if self._on_error:
            await self._on_error(update, exc)

    def set_callback(self, callback: Callable[[UT, ...], Coroutine[...]]):
        """Register new handler callback.
        It will be called during the new Update process after confirming the :meth:`check_new_update` function.

        Parameters
        ----------
            callback: Callable[[UT, ...], Coroutine[...]]
                The new callback function.
        """
        self._callback = callback

    async def check_new_update(self, update: "Update") -> Optional[Tuple]:
        """This function determines whether the "update" should be covered by the handler or not.

        Parameters
        ----------
            update: :class:`bale.Update`
                The update to be tested.

        Returns
        -------
            If :obj:`False` or :obj:`None` is returned, the update should not be wrapped by the handler,
            otherwise the handler is required to wrapp that update.
        """
        return (
            update,
        )

    def error(self, func: ER) -> ER:
        """
        A decorator to set the `on_error` function for a handler.

         .. code:: python

                from bale import Update, Message
                from bale.handlers import MessageHandler

                ...

                @bot.handle(MessageHandler())
                async def message_handler(message: Message):
                    return await message.reply("Hello World!")

                @message_handler.error
                async def message_handler_error(update: Update, exc: Exception):
                    if update.message:
                        return
                    return await update.message.reply("The handler encountered an error")

        """
        self._on_error = func
        return self

    async def handle_update(self, update: "Update", *args):
        """This function works if the handler is required to cover the new Update and calls the :attr:`callback` function.

        Parameters
        ----------
            update: :class:`bale.Update`
                The update to be tested.
            args:
                Additional objects, if given to this parameter, will be passed directly to the :attr:`callback` function.
        """
        if self.callback:
            try:
                if self is BaseHandler:
                    return await self.callback(update)
                return await self.callback(*args)
            except Exception as exc:
                return await self._on_error(update, exc)
