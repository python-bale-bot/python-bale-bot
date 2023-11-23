from __future__ import annotations
from typing import Union, Optional
from . import InlineKeyboardButton, MenuKeyboardButton

class ReplyMarkupItem:
    __slots__ = (
        "_item",
        "_row"
    )
    def __init__(self, item: Union[InlineKeyboardButton, MenuKeyboardButton], row: Optional[int]=1):
        if not isinstance(item, (InlineKeyboardButton, MenuKeyboardButton)):
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
    def item(self) -> Union[InlineKeyboardButton, MenuKeyboardButton]:
        return self._item