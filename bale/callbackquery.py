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
from bale import BaleObject, User, Message
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "CallbackQuery"
)


class CallbackQuery(BaleObject):
    """
    This object represents an incoming callback query from a callback button in an inline keyboard.

    Attributes
    ----------
        id: :class:`str`
            Unique identifier for this query.
        from_user: :class:`bale.User`
            Sender.
        message: Optional[:class:`bale.Message`]
            Message with the callback button that originated the query. Note that message content and message date will not be available if the message is too old.
        inline_message_id: Optional[:class:`str`]
            Identifier of the message sent via the bot in inline mode, that originated the query.
        data: Optional[:class:`str`]
             Data associated with the callback button. Be aware that the message, which originated the query, can contain no callback buttons with this data.
    """
    __slots__ = (
        "id",
        "from_user",
        "message",
        "inline_message_id",
        "data"
    )

    def __init__(
            self, id: str, from_user: "User",
            data: Optional[str], message: Optional["Message"],
            inline_message_id: Optional[str]
    ):
        super().__init__()
        self._id = id
        self.id = id
        self.from_user = from_user

        self.data = data
        self.message = message
        self.inline_message_id = inline_message_id

    @property
    def user(self):
        """Aliases for :attr:`from_user`"""
        return self.from_user

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot: "Bot"):
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data['from_user'] = User.from_dict(data.pop('from', None), bot)
        data['message'] = Message.from_dict(data.get('message'), bot)

        return super().from_dict(data, bot)