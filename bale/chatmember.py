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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot

from bale import Permissions, User, ChatMemberStatus

__all__ = (
    "ChatMember",
)

class ChatMember:
    """This object shows a member in chat

    Attributes
    ----------
        user: :class:`bale.User`
            Information about the user.
        status: :class:`str`
            The member’s status in the chat.
        permissions: :class:`bale.Permissions`
            The member’s permissions in the chat.
    """
    __slots__ = (
        "chat_id", "status", "user", "permissions", "bot"
    )

    def __init__(self, chat_id: int, status: str, user: "User", permissions: "Permissions", bot: "Bot"):
        self.chat_id = chat_id
        self.status = status
        self.user = user
        self.permissions = permissions
        self.bot = bot

    @property
    def parsed_status(self) -> "ChatMemberStatus":
        """:class:`bale.ChatMemberStatus`: Represents the parsed member's status."""
        return ChatMemberStatus(self.status)

    async def ban(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.ban_chat_member`.

        .. code:: python

            member = await bot.get_chat_member(1234, 1234)
            await member.ban()
        """
        return await self.bot.ban_chat_member(self.chat_id, self.user.user_id)

    @classmethod
    def from_dict(cls, chat_id: int, data: dict, bot: "Bot"):
        return cls(chat_id=chat_id, permissions=Permissions.from_dict(data), user=User.from_dict(data.get("user")),
                   status=data.get("status"), bot=bot)

    def __repr__(self):
        return f"<ChatMember chat_id={self.chat_id} status={self.status} user={self.user} permissions={self.permissions}>"
