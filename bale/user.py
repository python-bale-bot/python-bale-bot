"""
    MIT License

    Copyright (c) 2022 kian Ahmadian

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
    from bale import Bot, Photo


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

    def __init__(self, user_id: int, first_name: str, last_name: str = None, username: str = None, bot: 'Bot' = None):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id
        self.bot = bot

    @property
    def mention(self) -> str | None:
        """Optional[:class:`str`]"""
        return f"@{self.username}" if self.username else None

    async def send(self, text: str, components=None):
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
        """
        return await self.bot.send_message(self, text, components)

    async def send_photo(self, photo: bytes | str | "Photo", caption: str = None):
        """For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        Parameters
        ----------
            photo: :class:`bytes` | :class:`str` | :class:`bale.Photo`
                Photo
            caption: :class:`str`
                Message caption
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            :class:`bale.Message`
                On success, the sent Message is returned.
        """
        return await self.bot.send_photo(self, photo, caption)

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
