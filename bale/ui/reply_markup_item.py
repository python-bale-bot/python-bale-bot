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
from typing import Union, Optional
from . import InlineKeyboardButton, MenuKeyboardButton

class ReplyMarkupItem:
    __slots__ = (
        "_item",
        "_row"
    )
    def __init__(self, item: Union[InlineKeyboardButton, MenuKeyboardButton], row: Optional[int]=1):
        """This object represents a Reply Markup Item.

        .. warning::
            Your numbers in the "row" param must be natural and greater than 0.

        Parameters
        ----------
            item: Union[:class:`InlineKeyboardButton`, :class:`MenuKeyboardButton`]
                The reply markup item.

            row: Optional[:class:`int`]
                The row of item.
        """
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
        """Optional[:class:`int`]: The row of item."""
        return self._row

    @property
    def item(self) -> Union[InlineKeyboardButton, MenuKeyboardButton]:
        """Union[:class:`InlineKeyboardButton`, :class:`MenuKeyboardButton`]: The reply markup item."""
        return self._item