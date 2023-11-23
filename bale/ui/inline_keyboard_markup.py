from __future__ import annotations
from typing import Optional, Dict, Self
from . import BaseReplyMarkup, InlineKeyboardButton, ReplyMarkupItem

class InlineKeyboardMarkup(BaseReplyMarkup):
    def __init__(self):
        super().__init__()

    def add(self, inline_keyboard_button: "InlineKeyboardButton", row: Optional[int] = None) -> Self:
        if not isinstance(inline_keyboard_button, InlineKeyboardButton):
            raise TypeError(
                "inline_keyboard_button must be type of InlineKeyboardButton"
            )

        super()._add(inline_keyboard_button, row)
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
            "inline_keyboard": components
        }
        for group in super()._to_components():
            components.append([inline_button.to_dict() for inline_button in group])

        return payload