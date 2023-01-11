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
    Parameters
    ----------
        keyboards: List[:class:`bale.Keyboard`]
            keyboards
        inline_keyboards: List[:class:`bale.InlineKeyboard`]
            inline keyboards
    """

    __slots__ = (
        "_keyboards",
        "_inline_keyboards"
    )

    def __init__(self, keyboards=None, inline_keyboards=None):

        if keyboards and inline_keyboards:
            raise TypeError("Your can't use keyboard and inline_keyboards params together.")

        if not (isinstance(keyboards, list) or isinstance(inline_keyboards, list)):
            raise TypeError("The type of parameter entered is incorrect.")

        self._keyboards = []
        self._inline_keyboards = []

        if keyboards:
            for obj in keyboards:
                if not isinstance(obj, (list, Keyboard)):
                    raise TypeError("object in keyboards param must be type of the list of Keyboard or a Keyboard.")
                self._keyboards.append(obj if isinstance(obj, list) else [obj])

        if inline_keyboards:
            for obj in inline_keyboards:
                if not isinstance(obj, (list, InlineKeyboard)):
                    raise TypeError("object in inline_keyboards param must be type of the list of Keyboard or a InlineKeyboard.")
                self._inline_keyboards.append(obj if isinstance(obj, list) else [obj])

    @classmethod
    def from_dict(cls, data: dict):
        return cls(keyboards=data["keyboard"], inline_keyboards=data["inline_keyboard"])

    def to_dict(self) -> Dict:
        data = {}
        keyboards = self._keyboards
        inline_keyboards = self._inline_keyboards

        if bool(keyboards):
            data["keyboard"] = [[k.to_dict() for k in obj] for obj in keyboards]

        if bool(inline_keyboards):
            data["inline_keyboard"] = [[ik.to_dict() for ik in obj] for obj in inline_keyboards]

        return data


class InlineKeyboard:
    """This object shows an inline keyboard (within the message).

    Attributes
    ----------
        text: str
            Label text on the button.
        callback_data: str
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        url: str
            HTTP url to be opened when the button is pressed. Defaults to None.
        switch_inline_query: str
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        switch_inline_query_current_chat: str
            If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field. Can be empty,
            in which case only the bot's username will be inserted. Defaults to None.
    """
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, *, callback_data: str = None, url: str = None, switch_inline_query: str = None,
                 switch_inline_query_current_chat: str = None):
        self.text = text
        self.callback_data = callback_data if callback_data is not None else None
        self.url = url if url is not None else None
        self.switch_inline_query = switch_inline_query if switch_inline_query is not None else switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat if switch_inline_query_current_chat is not None else None

    @classmethod
    def from_dict(cls, data: dict):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text=data["text"], callback_data=data.get("callback_data"), url=data.get("url"),
                   switch_inline_query=data.get("switch_inline_query"),
                   switch_inline_query_current_chat=data.get("switch_inline_query_current_chat"))

    def to_dict(self) -> dict:
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

    Attributes
    ----------
        text: str
            Keyboard Text.
    """
    __slots__ = (
        "text"
    )

    def __init__(self, text: str):
        self.text = text

    @classmethod
    def from_dict(cls, data: dict):
        if not data.get("text"):
            return None
        return cls(text=data["text"])

    def to_dict(self):
        data = {
            "text": self.text
        }
        return data


class RemoveComponents:
    """This object shows a remove keyboard."""

    def to_dict(self) -> dict:
        return {"keyboard": None}
