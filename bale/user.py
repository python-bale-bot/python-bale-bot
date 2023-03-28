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
    from bale import Bot, Photo, Document, Components, RemoveComponents, Price, Location, ContactMessage


class User:
    """This object represents a Bale user or bot.

    Attributes
    ----------
        user_id: int
            Unique identifier for this user or bot.
        is_bot: bool
            ``True``, if this user is a bot.
        first_name: str
            User’s or bot’s first name.
        last_name: Optional[:class:`str`]
            User’s or bot’s last name.
        username: Optional[:class:`str`]
            User’s or bot’s username.
    """
    __slots__ = (
        "is_bot",
        "first_name",
        "last_name",
        "username",
        "user_id",
        "bot"
    )

    def __init__(self, user_id: int, is_bot: bool, first_name: str, last_name: Optional[str] = None, username: Optional[str] = None,
            bot: 'Bot' = None):
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id
        self.bot = bot

    @property
    def mention(self) -> str | None:
        """Optional[:class:`str`]"""
        return f"@{self.username}" if self.username else None

    @property
    def chat_id(self) -> str:
        """:class:`str`"""
        return str(self.user_id)

    async def send(self, text: str, components: Optional["Components" | "RemoveComponents"] =None):
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

    async def send_location(self, location: "Location"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_location`.
        """
        return await self.bot.send_location(self.chat_id, location)

    async def send_contact(self, contact: "ContactMessage"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.
        """
        return await self.bot.send_contact(self.chat_id, contact)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *, photo_url: Optional[str] = None,
               need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False, need_email: Optional[bool] = False,
               need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`
        """
        return await self.bot.send_invoice(self.chat_id, title, description, provider_token, prices,
                                           photo_url=photo_url, need_name=need_name, need_email=need_email,
                                           need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    @classmethod
    def from_dict(cls, data: dict, bot=None):
        return cls(is_bot=data.get("is_bot"), username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   user_id=data.get("id"), bot=bot)

    def to_dict(self):
        data = {"is_bot": self.is_bot,
                "first_name": self.first_name if self.first_name is not None else None,
                "last_name": self.last_name if self.last_name is not None else None,
                "username": self.username if self.username is not None else None,
                "id": self.user_id if self.user_id is not None else None}

        return data

    def __str__(self):
        return (str(self.username) + "#" + str(self.user_id) if self.username else str(self.first_name) + " " + str(
            self.last_name))

    def __eq__(self, other: User):
        return isinstance(other, User) and self.user_id == other.user_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return f"<User is_bot={self.is_bot} first_name={self.first_name} last_name={self.last_name} user_id={self.user_id} username={self.username}>"
