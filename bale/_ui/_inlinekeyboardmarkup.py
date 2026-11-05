# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import ClassVar

from ._basereplymarkup import ReplyMarkup
from ._inlinekeyboardbutton import InlineKeyboardButton

__all__ = ("InlineKeyboardMarkup",)

Button = InlineKeyboardButton
ButtonList = list[Button]


class InlineKeyboardMarkup(ReplyMarkup[InlineKeyboardButton]):
    """Represents the matrix structure of inline buttons placed beneath a message.

    Methods support method chaining.

    Arguments:
        keyboards:
            Flexible input structure for defining the inline keyboard layout.
                Supported formats:

                * **A string:** Converted to a single-row inline keyboard containing one button with the given text.
                * **A button object** (:class:`InlineKeyboardButton`): Converted to a single-row inline keyboard containing that button.
                * **A list:** A list of rows, where each row can be:
                    * A string (creates a full-row button with that text).
                    * A button object (creates a full-row button).
                    * A list of buttons/strings (creates a multi-button row).
    """

    _button_cls = InlineKeyboardButton
    _payload: ClassVar = "inline_keyboard"
