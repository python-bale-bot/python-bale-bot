from __future__ import annotations
from typing import Dict

__all__ = (
    "Components",
    "Keyboard",
    "InlineKeyboard",
    "RemoveComponents"
)


class Components:
    """
        Args:
            keyboards (:class:`bale.Keyboards`): Defaults to None.
            inline_keyboards (:class:`bale.InlineKeyboards`): Defaults to None.
    """

    __slots__ = (
        "keyboards",
        "inline_keyboards"
    )

    def __init__(self, keyboards=None, inline_keyboards=None):

        if not (isinstance(keyboards, list) or isinstance(inline_keyboards, list)):
            raise TypeError("The type of parameter entered is incorrect.")

        self.keyboards = []
        self.inline_keyboards = []

        if keyboards:
            for obj in keyboards:
                if not isinstance(obj, list):
                    raise TypeError("object is not a list its a {}".format(obj.__class__))

                keyboard = [i.to_dict() for i in obj]
                self.keyboards.append(keyboard)

        if inline_keyboards:
            for obj in inline_keyboards:
                if not isinstance(obj, list):
                    raise TypeError("object is not a list its a {}".format(obj.__class__))

                inline_keyboard = [i.to_dict() for i in obj]
                self.inline_keyboards.append(inline_keyboard)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        return cls(keyboards=data["keyboard"], inline_keyboards=data["inline_keyboard"])

    def to_dict(self) -> Dict:
        """Convert Class to dict
            Returns:
                :dict:
        """
        data = {}
        keyboards = self.keyboards
        inline_keyboards = self.inline_keyboards

        if bool(keyboards):
            data["keyboard"] = keyboards

        if bool(inline_keyboards):
            data["inline_keyboard"] = inline_keyboards

        return data


class InlineKeyboard:
    """This object shows an in -line keyboard (within the message).

        Args:
            text (str):	Label text on the button.
            callback_data (str): If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
            url (str): HTTP url to be opened when the button is pressed. Defaults to None.
            switch_inline_query (str): If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
            switch_inline_query_current_chat (str): If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field. Can be empty, in which case only the bot's username will be inserted. Defaults to None.
    """
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, callback_data: str = None, url: str = None, switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None):
        self.text = text
        self.callback_data = callback_data if callback_data is not None else None
        self.url = url if url is not None else None
        self.switch_inline_query = switch_inline_query if switch_inline_query is not None else switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat if switch_inline_query_current_chat is not None else None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text=data["text"], callback_data=data.get("callback_data"), url=data.get("url"),
                   switch_inline_query=data.get("switch_inline_query"),
                   switch_inline_query_current_chat=data.get("switch_inline_query_current_chat"))

    def to_dict(self) -> dict:
        """Convert Class to dict
            Returns:
                :dict:
        """
        data = {
            "text": self.text
        }

        if self.callback_data:
            data["callback_data"] = self.callback_data

        if self.url:
            data["url"] = self.url

        if self.switch_inline_query:
            data["switch_inline_query"] = self.switch_inline_query

        if self.switch_inline_query_current_chat:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat

        return data


class Keyboard:
    """This object shows a keyboard

        Args:
            text (str): Keyboard Text.
    """
    __slots__ = (
        "text"
    )

    def __init__(self, text: str):
        self.text = text

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        if not data.get("text"):
            return None
        return cls(text=data["text"])

    def to_dict(self):
        """Convert Class to dict
        Returns:
            :dict:
        """
        data = {
            "text": self.text
        }
        return data


class RemoveComponents:
    """This object shows a remove keyboard"""

    def to_dict(self) -> dict:
        """Convert Class to dict
        Returns:
            :dict:
        """
        return {"inline_keyboard": None, "keyboard": None}
