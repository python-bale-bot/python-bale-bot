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
from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from bale import Bot, Message, User, Photo, Document, Components, RemoveComponents, Price


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
            Chat ID.
        _type: :class:`bale.ChatType`
            Chat Type.
        title: str
            Chat Title.
        username: str
            Chat Username (for DM or PV).
        first_name: str
            First name Chat (for DM or PV).
        last_name: str
            Last name Chat (for DM or PV).
        pinned_message: :class:`bale.Message`
            Pinned messages in chat. Defaults to None.
        all_members_are_administrators: bool
            Does everyone have admin access?. Defaults to True. (for Group)
        bot: :class:`bale.Bot`
            Bot Object. Defaults to None.

    .. container:: operations
        .. describe:: x == y
            Checks if two chat are equal.
        .. describe:: x != y
            Checks if two chat are not equal.
    """
    __slots__ = (
        "chat_id",
        "_type",
        "title",
        "username",
        "first_name",
        "last_name",
        "pinned_message",
        "all_members_are_administrators",
        "bot"
    )

    def __init__(self, chat_id: int | str, _type: "ChatType", title: str, username: str, first_name: str, last_name: str,
                 pinned_message: Message | None = None, all_members_are_administrators: bool = True, bot: 'Bot' = None):
        self.chat_id = chat_id
        self._type = _type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_message = pinned_message
        self.all_members_are_administrators = all_members_are_administrators
        self.bot = bot

    @property
    def type(self):
        """Get chat type"""
        return self._type

    @property
    def mention(self) -> str | None:
        """Optional[:class:`str`]"""
        return ("@" + self.username) if self.username else None

    async def send(self, text: str, components: Optional["Components" | "RemoveComponents"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        Parameters
        -----------
            text: str
                Message content
            components: Optional[:class:`bale.Components` | :class:`bale.RemoveComponents`]
                Message components
        Returns
        --------
            :class:`bale.Message`
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Message to this chat.
            APIError
                Send Message Failed.
        """
        return await self.bot.send_message(self, text, components=components)

    async def send_document(self, document: bytes | str | "Document", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        Parameters
        ----------
            document: :class:`bytes` | :class:`str` | :class:`bale.Document`
                Document
            caption: str
                Message caption.
        Returns
        -------
            Optional[:class:`bale.Message`]
                On success, the sent Message is returned.
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Document to this chat.
            APIError
                Send Document Failed.  
        """
        return await self.bot.send_document(self, document, caption=caption)

    async def send_photo(self, photo: bytes | str | "Photo", *, caption: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        Parameters
        ----------
            photo: :class:`bytes` | :class:`str` | :class:`bale.Photo`
                Photo
            caption: Optional[:class:`str`]
                Message caption
        Returns
        -------
            Optional[:class:`bale.Message`]
                On success, the sent Message is returned.
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Photo to chat.
            APIError
                Send Photo Failed.  
        """
        return await self.bot.send_photo(self, photo, caption=caption)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *,
                   photo_url: Optional[str] = None, need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False,
                       need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`

        Parameters
        ----------
            title: str
                Invoice Title
            description: str
                Invoice Description
            provider_token: str
                .. note::
                    You can use 3 methods to receive money:
                        * Card number
                        * Port number and acceptor number
                        * Wallet number "Bale"
            prices: List[:class:`bale.Price`]
                A list of prices.
            photo_url: Optional[:class:`str`]
                Photo URL of Invoice.
            need_name: Optional[:class:`bool`]
                Get a name from "User"?
            need_phone_number: Optional[:class:`bool`]
                Get a Phone number from "User"?.
            need_email: Optional[bool]
                Get a Email from "User"?.
            need_shipping_address: Optional[bool]
                Get a Shipping Address from "User"?.
            is_flexible: Optional[bool]
                Is the Invoice Photo Flexible to the Payment button?
        Returns
        -------
            :class:`Bale.Message`:
                On success, the message sent returned.
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Invoice to this chat.
            APIError
                Send Invoice Failed.  
        """
        return await self.bot.send_invoice(chat=self, title=title, description=description,
                                        provider_token=provider_token, prices=prices, photo_url=photo_url,
                                        need_name=need_name, need_email=need_email, need_phone_number=need_phone_number,
                                        need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    async def leave(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.leave_chat`.

        Raises
        ------
            Forbidden
                You do not have permission to Leave from chat.
            APIError
                Leave from chat Failed.
        """
        await self.bot.leave_chat(self)

    async def add_user(self, user: "User"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.invite_to_chat`.

        Parameters
        ----------
            user: :class:`bale.User`
                user
        Raises
        ------
            NotFound
                Invalid User.
            Forbidden
                You do not have permission to Add user to Chat.
            APIError
                Invite user Failed.
        """
        await self.bot.invite_to_chat(self, user)

    async def get_chat_member(self, user: "User" | str):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_member`.

        Parameters
        ----------
            user: :class:`bale.User`
                User

        Returns
        -------
            Optional[:class:`bale.ChatMember`]:
                The chat member or ``None`` if not found.

        Raises
        ------
            NotFound
                Invalid User.
            Forbidden
                You do not have permission to get Chat Member.
            APIError
                Get chat member Failed.
        """
        if not isinstance(user, (User, str)):
            raise TypeError("user must be type of user or str")

        if isinstance(user, User):
            user = user.user_id

        return await self.bot.get_chat_member(self, user_id=user)

    async def get_chat_members_count(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_members_count`.

        Returns
        -------
            :class:`int`
                The members count of the chat.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to get Members count of the Chat.
            APIError
                get Members count of the Chat Failed.
        """
        return await self.bot.get_chat_members_count(self)

    async def get_chat_administrators(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_administrators`.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to get Administrators of the Chat.
            APIError
                get Administrators of the Chat from chat Failed.
        Returns
        -------
            Optional[List[:class:`bale.ChatMember`]]
                On success, The chat members is returned.
        """
        return await self.bot.get_chat_administrators(self)

    @classmethod
    def from_dict(cls, data: dict, bot):
        return cls(bot=bot, chat_id=data.get("id"), _type=ChatType(data.get("type")), title=data.get("title"),
                   username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   pinned_message=Message.from_dict(bot=bot, data=data.get("pinned_message")) if data.get("pinned_message") else None,
                   all_members_are_administrators=data.get("all_members_are_administrators", True))

    def to_dict(self):
        data = {
            "id": self.chat_id,
            "type": self.type,
            "title": self.title,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
        if self.pinned_message:
            data["pinned_message"] = self.pinned_message.to_dict()

        return data

    def __str__(self):
        return (str(self.username) + "#" + str(self.chat_id) if self.username else str(self.first_name) + " " + str(
            self.last_name))

    def __eq__(self, other):
        return isinstance(other, Chat) and self.chat_id == other.chat_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return (f"<Chat type={self._type} first_name={self.first_name} last_name={self.last_name} user_id={self.chat_id} username={self.username}"
            f"title={self.title}>")
