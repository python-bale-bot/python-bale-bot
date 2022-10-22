from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Dict
from bale import (Message, CallbackQuery)
if TYPE_CHECKING:
    from bale import Bot


class UpdateType:
    """Update Type"""
    MESSAGE = "message"
    CALLBACK = "callback_query"
    UNKNOWN = "unknown"


class Update:
    """This object shows an update.

    Attributes
    ----------
        update_id: int
            Update ID
        type: str
            Chat type
        callback_query: Optional[:class:`bale.CallbackQuery`]
            Callback Query
        message: Optional[:class:`bale.Message`]
            Message
        edited_message: Optional[:class:`bale.Message`]
            Edited Message
    """
    __slots__ = (
        "update_id",
        "_type",
        "message",
        "callback_query",
        "edited_message",
        "bot",
        "raw_data"
    )

    def __init__(self, update_id: int, callback_query: "CallbackQuery" = None, message: "Message" = None,
                 edited_message: "Message" = None, bot: 'Bot' = None, raw_data: dict = None):
        self.update_id = int(update_id)
        self.bot = bot
        self.raw_data = raw_data
        self.callback_query = callback_query if callback_query is not None else None
        self.message = message if message is not None else None
        self.edited_message = edited_message if edited_message is not None else None

    @property
    def type(self) -> Literal['callback_query', 'message', 'unknown']:
        if self.callback_query is not None:
            return "callback_query"
        elif self.message is not None:
            return "message"
        return "unknown"

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        callback_query, message, edited_message = None, None, None

        if data.get("callback_query"):
            callback_query = CallbackQuery.from_dict(data.get("callback_query"), bot=bot)
        if data.get("message"):
            message = Message.from_dict(data.get("message"), bot=bot)
        if data.get("edited_message"):
            edited_message = Message.from_dict(data=data.get("edited_message"), bot=bot)

        return cls(update_id=data["update_id"], message=message, callback_query=callback_query, edited_message=edited_message,
                   raw_data=data, bot=bot)

    def to_dict(self) -> Dict:
        data = {}

        if self.type:
            data["type"] = self.type
        if self.callback_query:
            data["callback_query"] = self.callback_query.to_dict()
        if self.message:
            data["message"] = self.message.to_dict()
        if self.edited_message:
            data["edited_message"] = self.edited_message.to_dict()

        return data

    def __eq__(self, other):
        return isinstance(other, Update) and self.update_id == other.update_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id <= other.update_id

    def __ge__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id >= other.update_id

    def __lt__(self, other):
        if not isinstance(other, Update):
            raise NotImplemented

        return self.update_id < other.update_id

    def __gt__(self, other):
        return not self.__lt__(other)

    def __repr__(self):
        return f"<Update type={self.type} message={self.message}>"
