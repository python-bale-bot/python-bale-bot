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
from bale import (Message, CallbackQuery)

if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "Update",
)


def parse_type(data: Dict) -> Optional[str]:
    events = ("callback_query", "edited_message", "message")
    for event in events:
        if data.get(event):
            return event

    return None

class Update:
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
    __slots__ = (
        "update_id",
        "type",
        "message",
        "callback_query",
        "edited_message",
        "bot"
    )

    def __init__(self, update_id: int, type: Optional[str], callback_query: "CallbackQuery" = None, message: "Message" = None,
                 edited_message: "Message" = None, bot: 'Bot' = None):
        self.update_id = int(update_id)
        self.type = type
        self.bot = bot
        self.callback_query = callback_query if callback_query is not None else None
        self.message = message if message is not None else None
        self.edited_message = edited_message if edited_message is not None else None

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        callback_query, message, edited_message = None, None, None
        update_type: Optional[str] = parse_type(data)

        if update_type == "callback_query":
            callback_query = CallbackQuery.from_dict(data[update_type], bot=bot)
        if update_type == "message":
            message = Message.from_dict(data[update_type], bot=bot)
        if update_type == "edited_message":
            edited_message = Message.from_dict(data[update_type], bot=bot)

        return cls(type=update_type, update_id=data["update_id"],
                   message=message, callback_query=callback_query, edited_message=edited_message, bot=bot)

    def to_dict(self) -> Dict:
        data = {}

        if self.type:
            data["type"] = self.type
        if self.callback_query:
            data["callback_query"] = self.callback_query.to_dict()
        if self.message:
            data["message"] = self.message.to_dict()

        return data

    def __eq__(self, other):
        return isinstance(other, Update) and self.update_id == other.update_id

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def __repr__(self):
        return f"<Update update_id={self.update_id} type={self.type}>"
