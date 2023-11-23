from __future__ import annotations
from typing import Optional, Dict, List
from . import BaseReplyMarkup, MenuKeyboardButton, ReplyMarkupItem

class MenuKeyboardMarkup(BaseReplyMarkup):
    def __init__(self, inline_keyboards: List["ReplyMarkupItem"]):
        super().__init__()

    def add(self, keyboard_button: MenuKeyboardButton, row: Optional[int] = None):
        if not isinstance(keyboard_button, MenuKeyboardButton):
            raise TypeError(
                "keyboard_button param must be type of KeyboardButton"
            )

        super()._add(keyboard_button, row)

    def to_dict(self) -> Dict:
        components = []
        payload = {
            "keyboard": components
        }
        for group in super()._to_components():
            components.append([keyboard_button.to_dict() for keyboard_button in group])

        return payload