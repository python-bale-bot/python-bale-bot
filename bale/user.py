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
    from bale import Bot, Photo, Document, Components, RemoveComponents, Price


class User:
    """This object shows a user.

    Attributes
    ----------
        user_id: int
        first_name: str
        last_name: str
        username: Optional[:class:`str`]
    """
    __slots__ = (
        "first_name",
        "last_name",
        "username",
        "user_id",
        "bot"
    )

    def __init__(self, user_id: int, first_name: str, last_name: str = None, username: str = None,
            bot: 'Bot' = None):
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

        Parameters
        ----------
            text: str
                Message Content
            components: :class:`bale.Components` | :class:`bale.RemoveComponents`
                Message Components
        Returns
        -------
            :class:`bale.Message`
                On success, the sent Message is returned.
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

    async def send_document(self, document: bytes | str | "Document", *,
            caption: Optional[str] = None):
        """For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        Parameters
        ----------
            document: :class:`bytes` | :class:`str` | :class:`bale.Document`
                Photo
            caption: :class:`str`
                Message caption
        Returns
        -------
            :class:`bale.Message`
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
        """For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        Parameters
        ----------
            photo: :class:`bytes` | :class:`str` | :class:`bale.Photo`
                Photo
            caption: Optional[:class:`str`]
                Message caption
        Returns
        -------
            :class:`bale.Message`
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

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *, photo_url: Optional[str] = None,
               need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False, need_email: Optional[bool] = False,
               need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
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
                                           need_name=need_name, need_email=need_email,
                                           need_phone_number=need_phone_number,
                                           need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    @classmethod
    def from_dict(cls, data: dict, bot=None):
        return cls(username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   user_id=data.get("id"), bot=bot)

    def to_dict(self):
        data = {"first_name": self.first_name if self.first_name is not None else None,
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
        return f"<User first_name={self.first_name} last_name={self.last_name} user_id={self.user_id} username={self.username}>"
