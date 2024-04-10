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
from typing import Optional, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot

from bale import BaleObject

class InlineKeyboardButton(BaleObject):
    """This object shows an inline keyboard button (within the message).

    Attributes
    ----------
        text: str
            Label text on the button.
        callback_data: :obj:`str`, optional
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        url: :obj:`str`, optional
            HTTP url to be opened when the button is pressed. Defaults to None.
        switch_inline_query: :obj:`str`, optional
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        switch_inline_query_current_chat: :obj:`str`, optional
            If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field. Can be empty,
            in which case only the bot's username will be inserted. Defaults to None.
    """
    __slots__ = (
        "text",
        "callback_data",
        "url",
        "switch_inline_query",
        "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, *, callback_data: Optional[str] = None, url: Optional[str] = None, switch_inline_query: Optional[str] = None,
                 switch_inline_query_current_chat: str = None):
        super().__init__()
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat

        self._lock()

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot: "Bot") -> Optional["InlineKeyboardButton"]:
        data = BaleObject.parse_data(data)
        if not data:
            return None


        data["callback_data"] = data.get("callback_data")
        data["url"] = data.get("url")
        data["switch_inline_query"] = data.get("switch_inline_query")
        data["switch_inline_query_current_chat"] = data.get("switch_inline_query_current_chat")

        return super().from_dict(data, bot)
