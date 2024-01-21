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
from typing import Optional, Dict
from . import BaseReplyMarkup, InlineKeyboardButton, ReplyMarkupItem

class InlineKeyboardMarkup(BaseReplyMarkup):
    """
    .. admonition:: Examples

            :any:`Components Bot <examples.inlinemarkup>`
    """
    def __init__(self):
        super().__init__()

    def add(self, inline_keyboard_button: "InlineKeyboardButton", row: Optional[int] = None) -> "InlineKeyboardMarkup":
        """Add an Inline Keyboard button to keyboards.

        Parameters
        ----------
            inline_keyboard_button: :class:`bale.InlineKeyboardButton`
                The inline keyboard button.
            row: Optional[:class:`int`]
                The row where you want the button to be placed.

                .. warning::
                    Your numbers in the "row" param must be natural and greater than 0.
        """
        if not isinstance(inline_keyboard_button, InlineKeyboardButton):
            raise TypeError(
                "inline_keyboard_button must be type of InlineKeyboardButton"
            )

        super()._add(inline_keyboard_button, row)
        return self

    def remove(self, item: "ReplyMarkupItem") -> "InlineKeyboardMarkup":
        """Remove a Reply Markup item from keyboards.

        Parameters
        ----------
            item: :class:`bale.ReplyMarkupItem`
                The reply markup item.
        """
        super()._remove(item)
        return self

    def remove_row(self, row: int) -> "InlineKeyboardMarkup":
        """Remove a row along with the inline keyboards located in that row.

        Parameters
        ----------
            row: :class:`int`
                The row.

                .. warning::
                    Your numbers in the "row" param must be natural and greater than 0.
        """
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