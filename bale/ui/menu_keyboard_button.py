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
from typing import Optional

class MenuKeyboardButton:
    """This object shows a Keyboard Button

    Attributes
    ----------
        text: str
            Keyboard Text.
        request_contact: Optional[:class:`bool`]
            If ``True``, the user’s phone number will be sent as a contact when the button is pressed.
        request_location: Optional[:class:`bool`]
            If ``True``, the user’s current location will be sent when the button is pressed. Available in private chats only.
    """
    __slots__ = (
        "text",
        "request_contact",
        "request_location"
    )

    def __init__(self, text: str, *, request_contact: Optional[bool] = False, request_location: Optional[bool] = False):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location

    @classmethod
    def from_dict(cls, data: dict):
        return cls(text=data["text"], request_contact=data.get("request_contact", False), request_location=data.get("request_location", False))

    def to_dict(self):
        data = {
            "text": self.text
        }

        if self.request_contact:
            data["request_contact"] = self.request_contact
        if self.request_location:
            data["request_location"] = self.request_location
        return data