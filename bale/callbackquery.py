from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot
from bale import User, Message


class CallbackQuery:
    """This object represents an incoming callback query from a callback button in an inline keyboard.

        Args:
            id (int): Callback Query ID
            data (str): Callback Data
            message (:class:`bale.Message`): Callback Message
            inline_message_id (str): Callback inline message id
            from_user (:class:`bale.User`): Callback The user who gave the callback.
            bot (:class:`bale.Bot`): Defaults to None.
    """
    __slots__ = (
        "message",
        "inline_message_id",
        "from_user",
        "data",
        "bot",
        "id"
    )

    def __init__(self, id: int = None, data: str = None, message: "Message" = None, inline_message_id: str = None,
                 from_user: "User" = None, bot: "Bot" = None):
        self.data = data
        self.id = id
        self.message = message
        self.inline_message_id = inline_message_id
        self.from_user = from_user
        self.bot = bot

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        return cls(bot=bot, data=data["data"], id=data["id"], message=Message.from_dict(data["message"], bot=bot),
                   inline_message_id=data["inline_message_id"], from_user=User.from_dict(bot=bot, data=data["from"]))

    def to_dict(self):
        """Convert Class to dict
            Returns:
                :dict:
        """
        data = {
            "id": self.id
        }

        if self.data:
            data["data"] = self.data
        if self.inline_message_id:
            data["inline_message_id"] = self.inline_message_id
        if self.message:
            data["message"] = self.message.to_dict()
        if self.from_user:
            data["from_user"] = self.from_user.to_dict()

        return data
