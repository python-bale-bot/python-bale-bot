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
    from bale import Bot, Components, Price, Location, ContactMessage, InputFile


class User:
    """This object represents a Bale user or bot.

    Attributes
    ----------
        user_id: :class:`int`
            Unique identifier for this user or bot.
        is_bot: :class:`bool`
            ``True``, if this user is a bot.
        first_name: :class:`str`
            User’s or bot’s first name.
        last_name: Optional[:class:`str`]
            User’s or bot’s last name.
        username: Optional[:class:`str`]
            User’s or bot’s username.
    """
    __slots__ = (
        "__weakref__",
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
        """Optional[:class:`str`]: mention user with username."""
        return f"@{self.username}" if self.username else None

    @property
    def chat_id(self) -> str:
        """Aliases for :attr:`user_id`"""
        return str(self.user_id)

    async def send(self, text: str, components: Optional["Components"] =None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        .. code:: python

            await user.send("Hi, python-bale-bot!", components = None)
        """
        return await self.bot.send_message(self.chat_id, text, components=components)

    async def send_document(self, document: "InputFile", *, caption: Optional[str] = None, components: Optional["Components"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        .. code:: python

            await user.send_document(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_document(self.chat_id, document, caption=caption, components=components)

    async def send_photo(self, photo: "InputFile", *, caption: Optional[str] = None, components: Optional["Components"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        .. code:: python

            await user.send_photo(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_photo(self.chat_id, photo, caption=caption, components=components)

    async def send_video(self, video: "InputFile", *, caption: Optional[str] = None, components: Optional["Components"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.

        .. code:: python

            await user.send_video(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_video(self.chat_id, video, caption=caption, components=components)

    async def send_animation(self, animation: "InputFile", *, duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, caption: Optional[str] = None, components: Optional["Components"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_animation`.

        .. code:: python

            await user.send_animation(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_animation(self.chat_id, animation, duration=duration, width=width, height=height, caption=caption, components=components)

    async def send_audio(self, audio: "InputFile", *, caption: Optional[str] = None, components: Optional["Components"] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await user.send_audio(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_audio(self.chat_id, audio, caption=caption, components=components)

    async def send_location(self, location: "Location"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_location`.

        .. code:: python

            await user.send_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.bot.send_location(self.chat_id, location)

    async def send_contact(self, contact: "ContactMessage"):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.

        .. code:: python

            await user.send_contact(bale.ContactMessage('09****', 'first name', 'last name))
        """
        return await self.bot.send_contact(self.chat_id, contact)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["Price"], *, payload: Optional[str] = None,
               photo_url: Optional[str] = None, need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False,
               need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`.

        .. code:: python

            await user.send_invoice(
                "invoice title", "invoice description", "6037************", [bale.Price("label", 2000)],
                payload = "unique invoice payload", ...
            )
        """
        return await self.bot.send_invoice(self.chat_id, title, description, provider_token, prices,
                                           payload=payload, photo_url=photo_url, need_name=need_name, need_email=need_email,
                                           need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible)

    @classmethod
    def from_dict(cls, data: dict, bot=None):
        return cls(is_bot=data.get("is_bot"), username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   user_id=data.get("id"), bot=bot)

    def to_dict(self):
        data = {
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "id": self.user_id
        }

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
