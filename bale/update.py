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
from typing import TYPE_CHECKING, Dict, Optional
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
    CALLBACK_QUERY = "callback_query"
    MESSAGE = "message"
    EDITED_MESSAGE = "edited_message"
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
