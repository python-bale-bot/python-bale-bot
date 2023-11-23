from __future__ import annotations
from typing import Optional, Dict, List, Self
from . import BaseReplyMarkup, MenuKeyboardButton, ReplyMarkupItem

class MenuKeyboardMarkup(BaseReplyMarkup):
    def __init__(self, inline_keyboards: List["ReplyMarkupItem"]):
        super().__init__()

    def add(self, keyboard_button: MenuKeyboardButton, row: Optional[int] = None) -> Self:
        if not isinstance(keyboard_button, MenuKeyboardButton):
            raise TypeError(
                "keyboard_button param must be type of KeyboardButton"
            )

        super()._add(keyboard_button, row)
        return self

    def remove(self, item: "ReplyMarkupItem") -> Self:
        super()._remove(item)
        return self

    def remove_row(self, row: int) -> Self:
        super()._remove_row(row)
        return self

    def to_dict(self) -> Dict:
        components = []
        payload = {
            "keyboard": components
        }
        for group in super()._to_components():
            components.append([keyboard_button.to_dict() for keyboard_button in group])

        return payload