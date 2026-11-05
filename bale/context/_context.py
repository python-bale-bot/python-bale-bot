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

from typing import TYPE_CHECKING

from .._utils.typehint import MISSING, SentinelOrValue
from ._context_data import ContextData, ContextDataScope

if TYPE_CHECKING:
    from bale import (Bot, CallbackQuery, Chat, InlineKeyboardMarkup, Message,
                      ReplyKeyboardMarkup, Update, User)
    from bale.flow import ConversationFlow
    from bale.handlers import UpdateHandler
    from bale.storage import BaseStorage

__all__ = ("Context",)


class Context:
    """


    .. versionadded:: 3.0
    """

    __slots__ = (
        "bot",
        "update",
        "args",
        "handler",
        "flow",
        "_bot_data",
        "_user_data",
        "_chat_data",
        "_storage",
    )

    def __init__(
        self,
        /,
        bot: "Bot",
        update: "Update",
        args: list[str] | tuple[str],
        storage: "BaseStorage | None" = None,
        handler: "UpdateHandler | None" = None,
        flow: "ConversationFlow | None" = None,
    ) -> None:
        self.bot: "Bot" = bot
        self.update: "Update" = update
        if isinstance(args, tuple):
            args = list(args)
        self.args: list[str] = args
        self._storage: "BaseStorage | None" = storage
        self.handler: "UpdateHandler | None" = handler
        self.flow: "ConversationFlow | None" = flow

        if storage:
            self._bot_data = ContextData(storage, ContextDataScope.BOT)
            if user := update.get_effective_user():
                self._user_data = ContextData(storage, ContextDataScope.USER, user.id)
            if chat := update.get_effective_chat():
                self._chat_data = ContextData(storage, ContextDataScope.CHAT, chat.id)

    def ensure_effective_user(self) -> "User":
        maybe_user = self.user
        if not maybe_user:
            raise RuntimeError(f"No user found for update {self.update}.")

        return maybe_user

    def ensure_effective_chat(self) -> "Chat":
        maybe_chat = self.chat
        if not maybe_chat:
            raise RuntimeError(f"No chat found for update {self.update}.")

        return maybe_chat

    def ensure_effective_message(self) -> "Message":
        maybe_message = self.message
        if not maybe_message:
            raise RuntimeError(f"No message found for update {self.update}.")

        return maybe_message

    def ensure_effective_callback_query(self) -> "CallbackQuery":
        maybe_callback_query = self.callback_query
        if not maybe_callback_query:
            raise RuntimeError(f"No callback query found for update {self.update}.")

        return maybe_callback_query

    @property
    def bot_data(self) -> ContextData | None:
        return self._bot_data

    @property
    def user_data(self) -> ContextData | None:
        return self._user_data

    @property
    def chat_data(self) -> ContextData | None:
        return self._chat_data

    @property
    def user(self) -> "User | None":
        return self.update.get_effective_user()

    @property
    def user_id(self) -> int | str | None:
        user = self.user
        if user and user.id:
            return user.user_id
        return None

    @property
    def chat(self) -> "Chat | None":
        return self.update.get_effective_chat()

    @property
    def chat_id(self) -> int | str | None:
        chat = self.chat
        if chat and chat.id:
            return chat.id
        return None

    @property
    def message(self) -> "Message | None":
        return self.update.get_effective_message()

    @property
    def message_id(self) -> int | str | None:
        message = self.update.get_effective_message()
        if message and message.message_id:
            return message.message_id
        return None

    @property
    def callback_query(self) -> "CallbackQuery | None":
        return self.update.callback_query

    @property
    def edited_message(self) -> "Message | None":
        return self.update.edited_message

    async def reply(
        self,
        text: str,
        *,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
        **kwargs,
    ) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.reply('This is a simple message!')
        """
        return await self.ensure_effective_message().reply(
            text, reply_markup=reply_markup, **kwargs
        )

    async def forward(self, chat_id: str | int, /, *args, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.forward(6429983203)
        """
        return await self.ensure_effective_message().forward(chat_id, **kwargs)

    async def send(self, /, *args, **kwargs) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.send('this is a edited message!')
        """
        return await self.ensure_effective_chat().send(*args, **kwargs)

    async def delete(self, /, *args, **kwargs) -> None:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.delete()
        """
        return await self.ensure_effective_message().delete(*args, **kwargs)

    async def edit_text(self, /, *args, **kwargs) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.edit('message edited!')
        """
        return await self.ensure_effective_message().edit_text(*args, **kwargs)

    async def edit_caption(self, /, *args, **kwargs) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.edit('message edited!')
        """
        return await self.ensure_effective_message().edit_caption(*args, **kwargs)

    async def edit_reply_markup(self, /, *args, **kwargs) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.edit('message edited!')
        """
        return await self.ensure_effective_message().edit_reply_markup(*args, **kwargs)

    async def answer_callback(self, /, *args, **kwargs) -> bool:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await ctx.answer_callback('I heard you clicking the button! 😄')
        """
        return await self.ensure_effective_callback_query().answer(*args, **kwargs)

    async def defer(self, /, *args, **kwargs) -> bool:
        """A shortcut for the :meth:`~bale.CallbackQuery.answer` method that releases
        the clicked inline keyboard button within the message from its loading state.

        The use of this method is recommended in cases where you intend to edit
        the original message or send a new one, as it clearly conveys to the user
        that the button-press command has been successfully received.

        """
        return await self.ensure_effective_callback_query().answer()

    @classmethod
    def from_update(cls, update: "Update", *args, **kwargs) -> "Context":
        return cls(bot=update.get_bot(), update=update, args=args, **kwargs)

    @classmethod
    def from_handler(
        cls, handler: "UpdateHandler", update: "Update", *args, **kwargs
    ) -> "Context":
        return cls(
            handler=handler, bot=update.get_bot(), update=update, args=args, **kwargs
        )

    @classmethod
    def from_flow(
        cls, flow: "ConversationFlow", update: "Update", *args, **kwargs
    ) -> "Context":
        return cls(flow=flow, bot=update.get_bot(), update=update, args=args, **kwargs)
