from __future__ import annotations
from typing import List, Union, Dict, Optional
from itertools import groupby
from . import ReplyMarkupItem, InlineKeyboardButton, KeyboardButton
from bale.utils import to_json

class BaseReplyMarkup:
    __slots__ = (
        "__keyboards"
    )
    def __init__(self):
        self.__keyboards: List["ReplyMarkupItem"] = []

    def _add(self, item: Union["InlineKeyboardButton", "KeyboardButton"], row: Optional[int]=None):
        reply_markup_item = ReplyMarkupItem(item, row)
        self.__keyboards.append(reply_markup_item)

    @property
    def keyboards(self) -> List["ReplyMarkupItem"]:
        return self.__keyboards

    def _to_components(self) -> List[List[Union["InlineKeyboardButton", "KeyboardButton"]]]:
        components = []
        def key(i: "ReplyMarkupItem"):
            return i.row

        for _, group in groupby(sorted(self.keyboards, key=key), key=key):
            components.append([i.item for i in group])

        return components

    def to_dict(self) -> Dict:
        return {}

    def to_json(self) -> str:
        return to_json(self.to_dict())