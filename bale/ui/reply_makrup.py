# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations
from typing import List, Union, Dict, Optional
from itertools import groupby
from . import ReplyMarkupItem, InlineKeyboardButton, MenuKeyboardButton
from bale.utils import to_json

class BaseReplyMarkup:
    __slots__ = (
        "__keyboards"
    )
    def __init__(self):
        self.__keyboards: List["ReplyMarkupItem"] = []

    def _add(self, item: Union["InlineKeyboardButton", "MenuKeyboardButton"], row: Optional[int]=None):
        reply_markup_item = ReplyMarkupItem(item, row)
        self.__keyboards.append(reply_markup_item)

    def _remove(self, item: "ReplyMarkupItem"):
        self.__keyboards.remove(item)

    def _remove_row(self, row: int):
        if not isinstance(row, int):
            raise TypeError(
                "row param must be type of number"
            )

        for item in self.__keyboards:
            if item.row == row:
                self.__keyboards.remove(item)

    @property
    def keyboards(self) -> List["ReplyMarkupItem"]:
        """List[:class:`bale.ReplyMarkupItem`]: The keyboards in order."""
        return self.__keyboards

    def _to_components(self) -> List[List[Union["InlineKeyboardButton", "MenuKeyboardButton"]]]:
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