from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot


class User:
    __slots__ = (
        "first_name",
        "last_name",
        "username",
        "user_id",
        "bot"
    )

    def __init__(self, user_id: int, first_name: str, last_name: str = None, username: str = None, bot: 'Bot' = None):
        """This object shows a user.

        Args:
            user_id (int): User ID.
            first_name (str): first user name
            last_name (str): last user name. Defaults to None.
            username (str): Username of the user. Defaults to None.
            bot (:class:`bale.Bot`): Bot Object. Defaults to None.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id
        self.bot = bot

    @property
    def link(self):
        if self.username:
            return "https://ble.ir/@{username}".format(username=self.username)
        return None

    def send(self, text: str, components=None):
        """:meth:`bale.Bot.send_message`

        Args:
            text (str): Message Text.
            components (Components, dict): Message Components. Defaults to None.
        Returns:
            :class:`bale.Message`
        """
        return self.bot.send_message(chat_id=str(self.user_id), text=text, components=components)

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
