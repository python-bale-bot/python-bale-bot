from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Dict
from bale import (Message, CallbackQuery)
if TYPE_CHECKING:
    from bale import Bot


class Update:
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
        """This object shows an update

        Args:
            update_id (int): Update ID
            callback_query (:class:`bale.CallbackQuery`): Defaults to None.
            message (:class:`bale.Message`): Defaults to None.
            edited_message (:class:`bale.Message`): Defaults to None.
            bot (:class:`bale.Bot`): Defaults to None.
            raw_data (dict): Defaults to None.
        """
        self.update_id = int(update_id)
        self.bot = bot
        self.raw_data = raw_data
        self.callback_query = None
        self.message = None
        self.edited_message = None
        if callback_query:
            self.callback_query = callback_query
            self.message: Message = self.callback_query.message
        elif message:
            self.message = message
        elif edited_message:
            self.edited_message = message

    @property
    def type(self) -> Literal['callback_query', 'message', 'unknown']:
        """Chat Type

        Returns:
            str: Literal['callback_query', 'message', 'unknown']
        """
        if self.callback_query is not None:
            return "callback_query"
        elif self.message is not None:
            return "message"
        return "unknown"

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        callback_query, message, edited_message = None, None, None
        if data.get("callback_query"):
            callback_query = CallbackQuery.from_dict(data.get("callback_query"), bot=bot)
            message = callback_query.message
        elif data.get("message"):
            message = Message.from_dict(data.get("message"), bot=bot)
        elif data.get("edited_message"):
            edited_message = Message.from_dict(data=data.get("edited_message"), bot=bot)

        return cls(update_id=data["update_id"], message=message, callback_query=callback_query, edited_message=edited_message,
                   raw_data=data, bot=bot)

    def to_dict(self) -> Dict:
        data = {}

        if self.type:
            data["type"] = self.type
        if self.callback_query:
            data["callback_query"] = self.callback_query.to_dict() if self.callback_query is not None else None
        if self.message:
            data["message"] = self.message.to_dict() if self.message is not None else None
        if self.edited_message:
            data["edited_message"] = self.edited_message.to_dict() if self.edited_message is not None else None

        return data
