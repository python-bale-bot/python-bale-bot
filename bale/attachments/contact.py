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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot, User


class ContactMessage:
    """This object shows a Message Contact.

    Attributes
    ----------
        phone_number: int
        first_name: Optional[:class:`str`]
        last_name: Optional[:class:`str`]
        user: Optional[:class:`bale.User`]
    """
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "id",
        "bot"
    )

    def __init__(self, phone_number: int, first_name: str = None, last_name: str = None, bot: "Bot" = None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.bot = bot

    @property
    def user(self):
        if self.id:
            return User(bot=self.bot, user_id=self.id, first_name=self.first_name, last_name=self.last_name)
        return None

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot" = None):
        return cls(first_name=data["first_name"], last_name=data["last_name"],
                   bot=bot, phone_number=data["phone_number"])

    def to_dict(self):
        data = {"phone_number": self.phone_number, "first_name": self.first_name, "last_name": self.last_name}

        return data
