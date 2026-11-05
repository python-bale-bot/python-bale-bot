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
from ._keyboardbutton import KeyboardButton

__all__ = ("ReplyKeyboardMarkup",)

Button = KeyboardButton
ButtonList = list[Button]


class ReplyKeyboardMarkup(ReplyMarkup[KeyboardButton]):
    """Represents a reply keyboard (menu buttons) displayed at the bottom of the chat.

    Methods return the object itself to allow method chaining.

    Note:
        If no keyboard is explicitly defined in the final state, a default button titled
        **Restart** is automatically added, which triggers the ``/start`` command.

        .. figure:: /_static/images/ui_remove_reply_keyboard.png
            :alt: Example of a message with a default keyboard menu
            :align: center
            :class: with-shadow
            :width: 480px

            **Figure** – Example of a message with a default keyboard menu

    Arguments:
        keyboards:
            Flexible input structure for defining the keyboard layout.
            Supported formats:

            * **A string:** Converted to a single-row keyboard containing one button with the given text.
            * **A button object** (:class:`.KeyboardButton`): Converted to a single-row keyboard containing that button.
            * **A list:** A list of rows, where each row can be:
                * A string (creates a full-row button with that text).
                * A button object (creates a full-row button).
                * A list of buttons/strings (creates a multi-button row).

    Keyword Arguments:
        resize_keyboard (:obj:`bool`, optional):
            Normally, the keyboard height is always fixed—regardless of the number of its rows. However, if this parameter is set to True, the keyboard height becomes dynamic and adjusts based on the number of keyboard rows, rather than using the default standard height.

    .. versionchanged:: 3.0
        The :paramref:`keyboards` parameter was added to allow inline initialization with flexible input types.
    """

    _button_cls = KeyboardButton
    _payload: ClassVar = "keyboard"
