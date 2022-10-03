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
from bale import Components
if TYPE_CHECKING:
    from bale import Bot


class User:
    """This object shows a user.
        Args:
            user_id (int): User ID.
            first_name (str): first user name
            last_name (str): last user name. Defaults to None.
            username (str): Username of the user. Defaults to None.
            bot (:class:`bale.Bot`): Bot Object. Defaults to None.
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
        """Mention User"""
        return f"@{self.username}" if self.username else None

    @property
    def link(self):
        """Get user link in bale"""
        if self.username:
            return "https://ble.ir/@{username}".format(username=self.username)
        return None

    async def send(self, text: str, components=None):
        """Send a Text Message to User

        Args:
            text (str): Message Text.
            components (:class:`bale.Components`|:class:`bale.RemoveComponents`): Message Components. Defaults to None.
        Returns:
            :class:`bale.Message`
        """
        from bale import Message
        if components:
            components = components.to_dict()
        response, payload = await self.bot.http.send_message(str(self.user_id), text, components=components)
        return Message.from_dict(data=payload["result"], bot=self.bot)

    async def send_photo(self, photo: bytes | str, caption: str = None):
        """This service is used to send photo.

        Args:
            photo (:class:`bytes`|:class:`str`): Photo.
            caption (:class:`str`): Message caption.
        Raises:
            :class:`bale.Error`
        Returns:
            :class:`bale.Message`: On success, the sent Message is returned.
        """
        from bale import Message
        if not isinstance(photo, (bytes, str)):
            raise TypeError(
                f"photo is not a str or bytes. this is a {photo.__class__} !"
            )

        response, payload = await self.bot.http.send_photo(str(self.user_id), photo, caption)
        return Message.from_dict(data=payload["result"], bot=self.bot)

    @classmethod
    def from_dict(cls, data: dict, bot=None):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        return cls(username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   user_id=data.get("id"), bot=bot)

    def to_dict(self):
        """Convert Class to dict
        Returns:
            :dict:
        """
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
