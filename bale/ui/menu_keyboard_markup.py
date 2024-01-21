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
from . import BaseReplyMarkup, MenuKeyboardButton, ReplyMarkupItem

class MenuKeyboardMarkup(BaseReplyMarkup):
    """
    .. admonition:: Examples

            :any:`Components Bot <examples.inlinemarkup>`
    """
    def __init__(self):
        super().__init__()

    def add(self, keyboard_button: MenuKeyboardButton, row: Optional[int] = None) -> "MenuKeyboardMarkup":
        """Add a Menu Keyboard button to keyboards.

        Parameters
        ----------
            keyboard_button: :class:`bale.MenuKeyboardButton`
                The menu keyboard button.
            row: Optional[:class:`int`]
                The row where you want the button to be placed.

                .. warning::
                    Your numbers in the "row" param must be natural and greater than 0.
        """
        if not isinstance(keyboard_button, MenuKeyboardButton):
            raise TypeError(
                "keyboard_button param must be type of KeyboardButton"
            )

        super()._add(keyboard_button, row)
        return self

    def remove(self, item: "ReplyMarkupItem") -> "MenuKeyboardMarkup":
        """Remove a Reply Markup item from keyboards.

        Parameters
        ----------
            item: :class:`bale.ReplyMarkupItem`
                The reply markup item.
        """
        super()._remove(item)
        return self

    def remove_row(self, row: int) -> "MenuKeyboardMarkup":
        """Remove a row along with the menu keyboards located in that row.

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
            "keyboard": components
        }
        for group in super()._to_components():
            components.append([keyboard_button.to_dict() for keyboard_button in group])
        if len(self.keyboards) <= 0:
            components.append([])

        return payload