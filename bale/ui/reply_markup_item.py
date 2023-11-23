from __future__ import annotations
from typing import Union, Optional
from . import InlineKeyboardButton, KeyboardButton

class ReplyMarkupItem:
    __slots__ = (
        "_item",
        "_row"
    )
    def __init__(self, item: Union[InlineKeyboardButton, KeyboardButton], row: Optional[int]=1):
        if not isinstance(item, (InlineKeyboardButton, KeyboardButton)):
            raise TypeError(
                "item param must be type of InlineKeyboardButton or KeyboardButton"
            )

        if not row:
            row = 1

        if not isinstance(row, int) or not row >= 1:
            raise TypeError(
                "row must be type of int and also a natural number"
            )

        self._item = item
        self._row = row

    @property
    def row(self) -> int:
        return self._row

    @property
    def item(self) -> Union[InlineKeyboardButton, KeyboardButton]:
        return self._item