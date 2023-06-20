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
from bale import User
from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from bale import Bot, Message, User, Photo, Document, Components, RemoveMenuKeyboard, Price, Location, ContactMessage, Video, Audio


__all__ = (
    "Chat",
    "ChatType"
)

class ChatType:
    """This object indicates a Chat Type.

    .. container:: operations
        .. describe:: x == y
            Checks if two chat type are equal.
        .. describe:: x != y
            Checks if two chat type are not equal.
    """
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"

    __slots__ = (
        "_type",
    )

    def __init__(self, _type: str):
        self._type = _type

    @property
    def type(self) -> str:
        return self._type

    def is_private_chat(self):
        """bool:
            Return ``True`` if Chat Type is Private"""
        return self._type == self.PRIVATE

    def is_group_chat(self):
        """bool:
            Return ``True`` if Chat Type is Group"""
        return self._type == self.GROUP

    def is_channel_chat(self):
        """bool:
            Return ``True`` if Chat Type is Channel"""
        return self._type == self.CHANNEL

    def __repr__(self):
        return f"<ChatType type={self.type}>"

    def __eq__(self, other):
        return self._type == other

    def __ne__(self, other):
        return not self.__eq__(other)

class Chat:
    """This object indicates a chat.

    Attributes
    ----------
        chat_id: str
            Unique identifier for this chat.
        type: :class:`bale.ChatType`
            Type of chat.
        title: Optional[:class:`str`]
            Title, for channels and group chats.
        username: Optional[:class:`str`]
            Username, for private chats, supergroups and channels if available.
        first_name: Optional[:class:`str`]
            First name of the other party in a private chat.
        last_name: Optional[:class:`str`]
            Last name of the other party in a private chat.
        pinned_message: Optional[:class:`bale.Message`]
            Pinned messages in chat. Defaults to None.
        invite_link: Optional[:class:`str`]
            Primary invite link, for groups and channel. Returned only in bale.Bot.get_chat().
        all_members_are_administrators: bool
            Does everyone have admin access?. Defaults to True. (for Group)

    .. container:: operations
        .. describe:: x == y
            Checks if two chat are equal.
        .. describe:: x != y
            Checks if two chat are not equal.
    """
    __slots__ = (
        "chat_id",
        "type",
        "title",
        "username",
        "first_name",
        "last_name",
        "pinned_message",
        "all_members_are_administrators",
        "invite_link",
        "bot"
    )

    def __init__(self, chat_id: int | str, type: "ChatType", title: Optional[str] = None, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None,
                 pinned_message: Optional["Message"] = None, all_members_are_administrators: Optional[bool] = None, invite_link: Optional[str] = None, bot: 'Bot' = None):
        self.chat_id = chat_id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_message = pinned_message
        self.all_members_are_administrators = all_members_are_administrators
        self.invite_link = invite_link
        self.bot = bot

    @property
    def mention(self) -> str | None:
        """Optional[:class:`str`]"""
        return ("@" + self.username) if self.username else None

    async def send(self, text: str, components: Optional["Components" | "RemoveMenuKeyboard"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.
        """
        return await self.bot.send_message(self.chat_id, text, components=components)

    async def send_document(self, document: bytes | str | "Document", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.
        """
        return await self.bot.send_document(self.chat_id, document, caption=caption)

    async def send_photo(self, photo: bytes | str | "Photo", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.
        """
        return await self.bot.send_photo(self.chat_id, photo, caption=caption)

    async def send_video(self, video: bytes | str | "Video", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.
        """
        return await self.bot.send_video(self.chat_id, video, caption=caption)

    async def send_audio(self, audio: bytes | str | "Audio", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.
        """
        return await self.bot.send_audio(self.chat_id, audio, caption=caption)

    async def send_location(self, location: "Location"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_location`.
        """
        return await self.bot.send_location(self.chat_id, location)

    async def send_contact(self, contact: "ContactMessage") -> "Message":
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.
        """
        return await self.bot.send_contact(self.chat_id, contact)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *,
                   photo_url: Optional[str] = None, need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False,
                       need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`
        """
        return await self.bot.send_invoice(self.chat_id, title, description, provider_token, prices,
                                        photo_url=photo_url, need_name=need_name, need_email=need_email,
                                        need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    async def leave(self):
        """
        For the documentation of the method, please see :meth:`bale.Bot.leave_chat`.
        """
        await self.bot.leave_chat(self.chat_id)

    async def add_user(self, user: "User"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.invite_user`.
        """
        await self.bot.invite_user(self.chat_id, user.chat_id)

    async def get_chat_member(self, user: "User" | str):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_member`.
        """
        if not isinstance(user, (User, str)):
            raise TypeError("user must be type of User or str")

        if isinstance(user, User):
            user = user.user_id

        return await self.bot.get_chat_member(self.chat_id, user_id=user)

    async def ban_chat_member(self, user: "User" | str):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.ban_chat_member`.
        """
        if not isinstance(user, (User, str)):
            raise TypeError("user must be type of user or str")

        if isinstance(user, User):
            user = user.user_id

        return await self.bot.ban_chat_member(self.chat_id, user_id=user)

    async def get_chat_members_count(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_members_count`.
        """
        return await self.bot.get_chat_members_count(self.chat_id)

    async def get_chat_administrators(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_administrators`.
        """
        return await self.bot.get_chat_administrators(self.chat_id)

    @classmethod
    def from_dict(cls, data: dict, bot):
        return cls(bot=bot, chat_id=data.get("id"), type=ChatType(data.get("type")), title=data.get("title"),
                   username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   pinned_message=Message.from_dict(bot=bot, data=data.get("pinned_message")) if data.get("pinned_message") else None,
                   all_members_are_administrators=data.get("all_members_are_administrators", True),
                   invite_link=data.get("invite_link"))

    def to_dict(self):
        data = {
            "id": self.chat_id,
            "type": self.type,
            "title": self.title,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

        return data

    def __str__(self):
        return str(self.first_name) + str(self.last_name)

    def __eq__(self, other):
        return isinstance(other, Chat) and self.chat_id == other.chat_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return (f"<Chat type={self.type} first_name={self.first_name} last_name={self.last_name} user_id={self.chat_id} username={self.username}"
            f"title={self.title}>")
