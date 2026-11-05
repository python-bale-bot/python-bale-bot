#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING

from .._baleobject import BaleObject

if TYPE_CHECKING:
    from bale import WebAppInfo

    from .._types.markup import KeyboardButton as KeyboardButtonPayload


class KeyboardButton(BaleObject):
    """Represents a single menu keyboard button displayed at the bottom of the chat.

    Attributes:
        text (:obj:`str`):
            The text label displayed on the button.
        request_contact (:obj:`bool`, optional):
            If evaluated to True, requests the user's contact details (upon permission), sending it via a new message update containing the :attr:`.Message.contact` attribute.
        request_location (:obj:`bool`, optional):
            If evaluated to True, requests the user's location details (upon permission), sending it via a new message update containing the :attr:`.Message.location` attribute.
        web_app (:obj:`bale.WebAppInfo`, optional):
            If present, opens the specified web page in a mini-app view.

            .. versionadded:: 3.0
        style (:obj:`str`, optional)
            If specified, it indicates the visual appearance of the button. It can be one of the colors red, green, or blue, as defined by the :class:`.constants.KeyboardButtonStyle` class.

            .. versionadded:: 3.0
    """

    __slots__ = ("text", "request_contact", "request_location", "web_app", "style")

    def __init__(
        self,
        text: str,
        *,
        request_contact: bool = False,
        request_location: bool = False,
        web_app: "WebAppInfo | None" = None,
        style: str | None = None,
    ) -> None:
        super().__init__()
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
        self.web_app = web_app
        self.style = style

        self._lock()

    @classmethod
    def from_dict(cls, data: "KeyboardButtonPayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaleObject.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["request_contact"] = parsed_data.get("request_contact", False)
        parsed_data["request_location"] = parsed_data.get("request_location", False)
        parsed_data["web_app"] = WebAppInfo.from_dict(parsed_data.get("web_app"), bot)

        return super().from_dict(parsed_data, bot)
