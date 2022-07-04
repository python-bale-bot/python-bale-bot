from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot, Message


class Chat:
    """This object indicates a chat.

        Args:
            chat_id (str): Chat ID.
            _type (str): Chat Type.
            title (str): Chat Title.
            username (str): Chat Username (for DM or PV).
            first_name (str): First name Chat (for DM or PV).
            last_name (str): Last name Chat (for DM or PV).
            pinned_messages (list[:class:`bale.Message`]): Pinned messages in chat. Defaults to [].
            all_members_are_administrators (bool): Does everyone have admin access?. Defaults to True. (for Group)
            bot (bale.Bot): Bot Object. Defaults to None.
    """
    PRIVATE = "private"
    GROUP = "group"

    __slots__ = (
        "chat_id",
        "_type",
        "title",
        "username",
        "first_name",
        "last_name",
        "pinned_messages",
        "all_members_are_administrators",
        "bot"
    )

    def __init__(self, chat_id: str, _type: str, title: str, username: str, first_name: str, last_name: str,
                 pinned_messages=None, all_members_are_administrators: bool = True, bot: 'Bot' = None):
        if pinned_messages is None:
            pinned_messages = []
        self.chat_id = str(chat_id)
        self._type = _type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_messages = pinned_messages
        self.all_members_are_administrators = all_members_are_administrators
        self.bot = bot

    @property
    def type(self):
        return self._type

    def send(self, text: str, components=None):
        """:meth:`bale.Bot.send_message`.

        Args:
            text (str): Message Text.
            components (:class:`bale.Components`, dict): Defaults to None.
        Returns:
            List(:class:`bale.Message`)
        """
        return self.bot.send_message(chat_id=self.chat_id, text=text, components=components)

    def get_chat_member(self, user_id: str):
        """:meth:`bale.Bot.get_chat_member`.

            Args:
                user_id (str): User ID.
            Returns:
                :class:`bale.ChatMember`
        """
        return self.bot.get_chat_member(chat_id=self.chat_id, user_id=user_id)

    def get_chat_members_count(self):
        """:meth:`bale.Bot.get_chat_members_count`.

            Returns:
                :int:
        """
        return self.bot.get_chat_members_count(chat_id=self.chat_id)

    def chat_administrators(self):
        """:meth:`bale.Bot.get_chat_administrators`.

        Raises:
            :class:`bale.Error`
        Returns:
            List[:class:`bale.ChatMember`]
        """
        return self.bot.get_chat_administrators(self.chat_id)

    @classmethod
    def from_dict(cls, data: dict, bot):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        pinned_messages = []
        if data.get("pinned_message") and isinstance(data["pinned_message"], list):
            for i in data["pinned_message"]:
                pinned_messages.append(Message.from_dict(bot=bot, data=i))
        return cls(bot=bot, chat_id=data.get("id"), _type=data.get("type"), title=data.get("title"),
                   username=data.get("username"), first_name=data.get("first_name"), last_name=data.get("last_name"),
                   pinned_messages=pinned_messages,
                   all_members_are_administrators=data.get("all_members_are_administrators", True))

    def to_dict(self):
        """Convert Class to dict
            Returns:
                :dict:
        """
        data = {}

        pinned_messages = []
        if isinstance(data.get("pinned_message"), list):
            for i in data.get("pinned_message", []):
                if isinstance(i, Message):
                    pinned_messages.append(i.to_dict())
                else:
                    pinned_messages.append(i)

        data["id"] = self.chat_id
        data["type"] = self._type
        data["title"] = self.title
        data["username"] = self.username
        data["first_name"] = self.first_name
        data["last_name"] = self.last_name
        data["pinned_message"] = pinned_messages

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
        return f"<Chat first_name={self.first_name} last_name={self.last_name} user_id={self.chat_id} username={self.username} title={self.title}>"
