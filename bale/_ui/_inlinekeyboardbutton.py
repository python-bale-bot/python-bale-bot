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

from typing import TYPE_CHECKING

from .. import BaleObject
from ._copytextbutton import CopyTextButton

if TYPE_CHECKING:
    from bale import WebAppInfo


class InlineKeyboardButton(BaleObject):
    """Represents an inline keyboard button (within the message).

    Important:
        Exactly **one** optional payload parameter (other than :attr:`text`) must be set at a time
        (e.g., :attr:`callback_data`, :attr:`url`, :attr:`web_app`, or :attr:`copy_text`).


    Attributes:
        text (:obj:`str`):
            The text label displayed on the button.
        callback_data (:obj:`str`, optional):
            If present, clicking the button sends a callback query update containing this data in :attr:`.CallbackQuery.data`.
        url (:obj:`str`, optional):
            If present, clicking the button redirects the user's client to the specified URL.
        web_app (:class:`~bale.WebAppInfo`, optional):
            If present, opens the specified web page in a mini-app view using a :class:`WebAppInfo` object.

            .. versionchanged:: 3.0
        copy_text (:class:`~bale.CopyTextButton`, optional):
            If present, clicking the button copies the predefined text string to the user's clipboard.

            .. versionchanged:: 3.0
        style (:obj:`str`, optional)
            If specified, it indicates the visual appearance of the button. It can be one of the colors red, green, or blue, as defined by the :class:`.constants.KeyboardButtonStyle` class.

            .. versionadded:: 3.0
    """

    __slots__ = ("text", "callback_data", "url", "web_app", "copy_text", "style")

    def __init__(
        self,
        text: str,
        *,
        callback_data: str | None = None,
        url: str | None = None,
        web_app: "WebAppInfo | None" = None,
        copy_text: "CopyTextButton | None" = None,
        style: str | None = None,
    ) -> None:
        super().__init__()
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.copy_text = copy_text
        self.style = style

        self._lock()
