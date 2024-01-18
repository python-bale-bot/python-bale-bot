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
from typing import TYPE_CHECKING, Dict, Optional, ClassVar
from bale import BaleObject, Message, CallbackQuery

if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "Update",
)

class Update(BaleObject):
    """This object represents an incoming update.

    Attributes
    ----------
        update_id: int
            The update’s unique identifier. Update identifiers start from a certain positive number and increase sequentially. This ID becomes especially handy if you’re using Webhooks, since it allows you to ignore repeated updates or to restore the correct update sequence, should they get out of order. If there are no new updates for at least a week, then identifier of the next update will be chosen randomly instead of sequentially.
        callback_query: Optional[:class:`bale.CallbackQuery`]
            New incoming callback query.
        message: Optional[:class:`bale.Message`]
            New incoming message of any kind - text, photo, sticker, etc.
        edited_message: Optional[:class:`bale.Message`]
            New version of a message that is known to the bot and was edited.
    """
    CALLBACK_QUERY: ClassVar[str] = "callback_query"
    MESSAGE: ClassVar[str] = "message"
    EDITED_MESSAGE: ClassVar[str] = "edited_message"
    __slots__ = (
        "update_id",
        "type",
        "message",
        "callback_query",
        "edited_message"
    )

    def __init__(self, update_id: int, callback_query: "CallbackQuery" = None, message: "Message" = None,
                 edited_message: "Message" = None):
        super().__init__()
        self._id = update_id
        self.update_id = int(update_id)
        self.callback_query = callback_query
        self.message = message
        self.edited_message = edited_message

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot: "Bot") -> Optional["Update"]:
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data['callback_query'] = CallbackQuery.from_dict(data.pop('callback_query', None), bot)
        data['message'] = Message.from_dict(data.pop('message', None), bot)
        data['edited_message'] = Message.from_dict(data.pop('edited_message', None), bot)

        return super().from_dict(data, bot)

    def __le__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id <= other.update_id

    def __ge__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id >= other.update_id

    def __lt__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id < other.update_id

    def __gt__(self, other):
        return not self.__lt__(other)
