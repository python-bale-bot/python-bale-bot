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
from bale import Permissions, User

__all__ = (
    "MemberRole",
    "ChatMember"
)


class MemberRole:
    """This object shows member's role in chat.

    .. container:: operations
        .. describe:: x == y
            Checks if two members role are equal.
        .. describe:: x != y
            Checks if two members role are not equal.
    """

    OWNER = "creator"
    CREATOR = OWNER
    ADMIN = "administrator"
    __slots__ = ("_role",)

    def __init__(self, _role: str):
        self._role = _role

    @property
    def role(self) -> str:
        return self._role

    def is_owner(self):
        """bool:
			Return ``True`` if Member is chat creator"""
        return self._role == self.OWNER

    def is_admin(self):
        """bool:
			Return ``True`` if Member have admin role"""
        return self._role == self.ADMIN

    def __repr__(self):
        return f"<MemberRole role={self.role}>"

    def __eq__(self, other):
        return self._role == other

    def __ne__(self, other):
        return not self.__eq__(other)


class ChatMember:
    """This object shows a member in chat

    Attributes
    ----------
        role: :class:`bale.MemberRole`
            User Role
        permissions: :class:`bale.AdminPermissions`
            User Permissions
    """
    __slots__ = (
        "chat_id", "role", "user", "permissions", "bot"
    )

    def __init__(self, chat_id: int, role: "MemberRole", user: "User", permissions: "Permissions", bot: "Bot"):
        self.chat_id = chat_id
        self.role = role
        self.user = user
        self.permissions = permissions
        self.bot = bot

    async def ban(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.ban_chat_member`.
        """
        return await self.bot.ban_chat_member(self.chat_id, self.user.user_id)

    @classmethod
    def from_dict(cls, chat_id: int, data: dict, bot: "Bot"):
        return cls(chat_id=chat_id, permissions=Permissions.from_dict(data), user=User.from_dict(data.get("user")),
                   role=MemberRole(data.get("status")), bot=bot)

    def __repr__(self):
        return f"<ChatMember chat_id={self.chat_id} role={self.role} user={self.user} permissions={self.permissions}>"
