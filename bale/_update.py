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

from ._baleobject import BaleObject
from ._callbackquery import CallbackQuery
from ._message import Message
from ._precheckoutquery import PreCheckoutQuery

if TYPE_CHECKING:
    from bale import Bot, Chat, User

    from ._types.update import Update as UpdatePayload

__all__ = ("Update",)


class Update(BaleObject):
    """This object represents an incoming update.

    Equality conditions:
        1. The second object must be an instance of the :class:`Update` class.
        2. Both must have the same :attr:`update_id`.

    Attributes:
        update_id (:obj:`int`):
            The update's unique identifier. Update identifiers start from a positive number and increase sequentially. This ID is especially useful when using webhooks, allowing duplicate updates to be ignored in case of out-of-order delivery.
        callback_query (:class:`~bale.CallbackQuery`, optional):
            New incoming callback query from a button press on an inline keyboard.
        message (:class:`~bale.Message`, optional):
            New incoming message of any kind - text, photo, sticker, etc.
        edited_message (:class:`~bale.Message`, optional):
            New incoming edited version of a previously sent message.
        pre_checkout_query (:class:`~bale.PreCheckoutQuery`, optional):
            New incoming pre-checkout query for wallet payments in Bale; when a user makes a payment, prior to finalizing the transaction and deducting the amount, an update containing this field is received so that the bot can verify it and respond within 10 seconds.

    .. versionchanged:: 3.0
        Added the :attr:`pre_checkout_query` attribute.
    """

    __slots__ = (
        "update_id",
        "type",
        "message",
        "callback_query",
        "edited_message",
        "pre_checkout_query",
    )

    def __init__(
        self,
        update_id: int,
        callback_query: "CallbackQuery | None" = None,
        message: "Message | None" = None,
        edited_message: "Message | None" = None,
        pre_checkout_query: "PreCheckoutQuery | None" = None,
    ) -> None:
        super().__init__()
        self._id = update_id
        self.update_id = int(update_id)
        self.callback_query = callback_query
        self.message = message
        self.edited_message = edited_message
        self.pre_checkout_query = pre_checkout_query

        self._lock()

    def get_effective_user(self) -> "User | None":
        """Returns the user who triggered the update."""
        if message := (self.message or self.edited_message):
            return message.author  # noqa
        if callback_query := self.callback_query:
            return callback_query.user

        return None

    def get_effective_chat(self) -> "Chat | None":
        """Returns the chat in which the update occurred."""
        if message := (self.message or self.edited_message):
            return message.chat  # noqa
        if (callback_query := self.callback_query) and callback_query.message:
            return callback_query.message.chat

        return None

    def get_effective_message(self) -> "Message | None":
        """Returns the message object associated with the update."""
        if message := (self.message or self.edited_message):
            return message  # noqa
        if callback_query := self.callback_query:
            return callback_query.message

        return None

    @classmethod
    def from_dict(cls, data: "UpdatePayload | None" = None, bot: "Bot | None" = None):
        """:meta private:"""
        parsed_data = BaleObject.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["callback_query"] = CallbackQuery.from_dict(
            parsed_data.pop("callback_query", None), bot
        )
        parsed_data["message"] = Message.from_dict(
            parsed_data.pop("message", None), bot
        )
        parsed_data["edited_message"] = Message.from_dict(
            parsed_data.pop("edited_message", None), bot
        )
        parsed_data["pre_checkout_query"] = PreCheckoutQuery.from_dict(
            parsed_data.pop("pre_checkout_query", None), bot
        )

        return super().from_dict(parsed_data, bot)

    def __eq__(self, other: object) -> bool:
        """If the unique identifier of an object update is the same as the unique identifier of another object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        """If the unique identifier of an object update is not the same as the unique identifier of another object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        return super().__ne__(other)

    def __le__(self, other: object) -> bool:
        """Only if the unique identifier of an object update is smaller than or equal to the unique identifier of another object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        if not isinstance(other, Update):
            return NotImplemented

        return self.update_id <= other.update_id

    def __ge__(self, other: object) -> bool:
        """Only if the unique identifier of an object update is greater than or equal to the unique identifier of another object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        if not isinstance(other, Update):
            return NotImplemented

        return self.update_id >= other.update_id

    def __lt__(self, other: object) -> bool:
        """Only if the unique identifier of an object update is smaller than the unique identifier of other object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        if not isinstance(other, Update):
            return NotImplemented

        return self.update_id < other.update_id

    def __gt__(self, other: object) -> bool:
        """Only if the unique identifier of an object update is greater than the unique identifier of other object, :obj:`True` is returned. Otherwise, :obj:`False` is returned."""
        if not isinstance(other, Update):
            return NotImplemented

        return self.update_id > other.update_id
