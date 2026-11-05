#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING

from ._baleobject import BaleObject
from ._message import Message
from ._user import User
from ._utils.typehint import MISSING, SentinelOrValue

if TYPE_CHECKING:
    from bale import Bot

    from ._types.callbackquery import CallbackQuery as CallbackQueryPayload

__all__ = ("CallbackQuery",)


class CallbackQuery(BaleObject):
    """This object represents an incoming callback query resulting from a user clicking an inline keyboard button in the Bale messenger.

    Equality Conditions:
        1. The second object must be an instance of the :class:`CallbackQuery` class.
        2. The unique identifiers of the callback queries (:attr:`id`) must be equal.

    Support for responding to inline buttons was added to Bale clients in June 2025
    (Khordad 1404), but it is not available in older Bale versions. Therefore, to prevent
    sending requests that older clients do not support, updates sent from old and new
    clients can be distinguished. Specifically, if the :attr:`id` of a callback query update begins with ``1``,
    it indicates that the user is using an older version (that client does not support this method).
    In python-bale-bot, every :class:`CallbackQuery` object has an attribute named
    :attr:`supports_answer_callback_query` to identify whether the client supports this method.

    Attributes:
        id (:obj:`str`):
            Unique identifier for this callback query.
        from_user (:class:`~bale.User`)
            Sender of the query (the user who clicked the button).
        chat_instance (:obj:`str`):
            Unique identifier for the chat associated with this callback query. It is always provided and, as long as :attr:`.Message.chat` is not populated in inline mode, it is used to compare between users.

            Note:
                 Currently, inline mode is not supported by Bale, but its presence is provided for completeness.
        message (:class:`~bale.Message`, optional):
            Message with the callback button that originated the query.

            Note:
                If the message is very old, its content or date may not be available.
        inline_message_id (:obj:`str`, optional):
            Identifier of the message sent via the inline mode originating the query.

            Note:
                 Currently, inline mode is not supported by Bale, but its presence is provided for completeness.
        data (:obj:`str`, optional):
            Data associated with the callback button. Be aware that a malicious user could send arbitrary data if the button was not properly configured.

    Note:
        Since clicking an inline button puts the button into a loading state on the client
        side for up to 5 seconds, it is strongly recommended to always respond to a callback
        query upon receiving it—even if none of the optional parameters of the :meth:`answer` method
        are used.
        For instance, when navigating users between different menus within the same message
        using inline buttons (Pagination), if this method is not called and only the message
        containing the clicked inline button is edited, the button will remain stuck in the
        loading state until you return from the secondary menu to the primary menu in some
        web client versions! (See the video below)

        .. video:: _static/images/use-answer-callback-query.mp4
                :preload: metadata

    """

    __slots__ = (
        "id",
        "from_user",
        "chat_instance",
        "message",
        "inline_message_id",
        "data",
    )

    def __init__(
        self,
        callback_id: str,
        from_user: "User",
        chat_instance: str,
        data: str | None = None,
        message: "Message | None" = None,
        inline_message_id: str | None = None,
    ) -> None:
        super().__init__()
        self._id = callback_id
        self.id = callback_id
        self.from_user = from_user
        self.chat_instance = chat_instance

        self.data = data
        self.message = message
        self.inline_message_id = inline_message_id

    @property
    def user(self):
        """Aliases for :attr:`from_user`"""
        return self.from_user

    @property
    def supports_answer_callback_query(self) -> bool:
        """Indicates whether the Bale client used by the user to click the button
        supports the :meth:`~bale.Bot.answer_callback_query` (:meth:`answer`) method or not.

        Returns:
             :obj:`True` if client supports :meth:`~bale.Bot.answer_callback_query`, :obj:`False` otherwise.

        .. versionadded:: 3.0
        """
        return not str(self.id).startswith("1")

    async def answer(
        self,
        text: SentinelOrValue[str] = MISSING,
        show_alert: SentinelOrValue[bool] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                if callback_query.supports_answer_callback_query:
                    await callback_query.answer("I heard you clicking the button!")

        .. versionadded:: 3.0
        """
        return await self.get_bot().answer_callback_query(
            self.id, text, show_alert, **kwargs
        )

    @classmethod
    def from_dict(
        cls, data: "CallbackQueryPayload | None" = None, bot: "Bot | None" = None
    ):
        """:meta private:"""
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["callback_id"] = data.pop("id")
        data["from_user"] = User.from_dict(data.pop("from", None), bot)
        data["message"] = Message.from_dict(data.get("message", None), bot)

        return super().from_dict(data, bot)
