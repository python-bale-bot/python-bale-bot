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
from ._chat import Chat
from ._chatphoto import ChatPhoto

if TYPE_CHECKING:
    from ._types.chat import ChatFullInfo as ChatFullInfoPayload

__all__ = ("ChatFullInfo",)


class ChatFullInfo(Chat):
    """This object contains full information about a chat.

    This object is used only when calling the :meth:`~bale.Bot.get_chat` method and
    contains more complete information than the standard :class:`Chat` object.
    Since it inherits from :class:`Chat`, you can also use the methods and
    attributes defined by that object.

    Attributes:
        id (:obj:`str`):
            Unique identifier for this chat.
        type (:obj:`str`):
            Type of chat.
        max_reaction_count (:obj:`int`):
            The maximum number of reactions that can be set on a message in the chat.
        title (:obj:`str`, optional):
            Title, for channels and group chats.
        username (:obj:`str`, optional):
            Username, for private chats and channels if available.
        first_name (:obj:`str`, optional):
            First name of the other party in a private chat.
        last_name (:obj:`str`, optional):
            Last name of the other party in a private chat.
        photo (:class:`~bale.ChatPhoto`, optional):
            Chat photo.
        invite_link (:obj:`str`, optional):
            Primary invite link, for groups and channel.
        linked_chat_id (:obj:`int`, optional):
            Unique identifier of the linked chat, where comments and discussion
            posts of the primary chat are located.
        bio (:obj:`str`, optional):
            Bio of the other party in a private chat.
        description (:obj:`str`, optional):
            Description, for groups and channel chats.

    See Also:
        :meth:`bale.Bot.get_chat`

    .. versionadded:: 3.0
    """

    __slots__ = (
        "photo",
        "description",
        "bio",
        "linked_chat_id",
        "pinned_message",
        "all_members_are_administrators",
        "invite_link",
        "max_reaction_count",
    )

    def __init__(
        self,
        chat_id: int,
        chat_type: str,
        max_reaction_count: int,
        title: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        description: str | None = None,
        bio: str | None = None,
        photo: "ChatPhoto | None" = None,
        invite_link: str | None = None,
        linked_chat_id: int | None = None,
    ) -> None:
        super().__init__(chat_id, chat_type, title, username, first_name, last_name)
        self._unlock()

        self.max_reaction_count = max_reaction_count
        self.photo = photo
        self.invite_link = invite_link
        self.description = description
        self.bio = bio
        self.linked_chat_id = linked_chat_id

        self._lock()

    async def get_linked_chat(self) -> ChatFullInfo | None:
        if _id := self.linked_chat_id:
            chat = await self.get_bot().get_chat(_id)
            return chat

        return None

    @classmethod
    def from_dict(cls, data: "ChatFullInfoPayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaleObject.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["chat_id"] = parsed_data.pop("id")
        parsed_data["chat_type"] = parsed_data.pop("type")
        parsed_data["photo"] = ChatPhoto.from_dict(parsed_data.get("photo"), bot)

        return super().from_dict(parsed_data, bot)

    def __eq__(self, other: object) -> bool:
        """
        :meta private:
        """
        if isinstance(other, Chat):
            return self._id == other._id

        return super().__eq__(other)
