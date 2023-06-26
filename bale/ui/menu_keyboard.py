from __future__ import annotations
from typing import Optional

class MenuKeyboard:
    """This object shows a Menu keyboard

    Attributes
    ----------
        text: str
            Keyboard Text.
        request_contact: bool
            If ``True``, the user’s phone number will be sent as a contact when the button is pressed.
        request_location: bool
            If ``True``, the user’s current location will be sent when the button is pressed. Available in private chats only.
    """
    __slots__ = (
        "text",
        "request_contact",
        "request_location"
    )

    def __init__(self, text: str, request_contact: Optional[bool] = False, request_location: Optional[bool] = False):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location

    @classmethod
    def from_dict(cls, data: dict):
        return cls(text=data["text"], request_contact=data.get("request_contact", False), request_location=data.get("request_location", False))

    def to_dict(self):
        data = {
            "text": self.text
        }

        if self.request_contact:
            data["request_contact"] = self.request_contact
        if self.request_location:
            data["request_location"] = self.request_location
        return data


class RemoveMenuKeyboard:
    """This object shows a Removed menu keyboard(s).

    .. code-block:: python3
    :caption: use RemoveMenuKeyboard to delete Menu keyboard Components.

    ...
    components = bale.RemoveMenuKeyboard()
    await message.reply(..., components=components)
    """

    def to_dict(self) -> dict:
        return {"keyboard": None}