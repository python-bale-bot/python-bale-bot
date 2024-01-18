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

class InlineKeyboardButton:
    """This object shows an inline keyboard button (within the message).

    Attributes
    ----------
        text: str
            Label text on the button.
        callback_data: Optional[:class:`str`]
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        url: Optional[:class:`str`]
            HTTP url to be opened when the button is pressed. Defaults to None.
        switch_inline_query: Optional[:class:`str`]
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified
            inline query in the input field. Can be empty, in which case just the bot's username will be inserted. Defaults to None.
        switch_inline_query_current_chat: Optional[:class:`str`]
            If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field. Can be empty,
            in which case only the bot's username will be inserted. Defaults to None.
    """
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat"
    )

    def __init__(self, text: str, *, callback_data: Optional[str] = None, url: Optional[str] = None, switch_inline_query: Optional[str] = None,
                 switch_inline_query_current_chat: str = None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat

    @classmethod
    def from_dict(cls, data: dict):
        return cls(text=data["text"], callback_data=data.get("callback_data"), url=data.get("url"),
                   switch_inline_query=data.get("switch_inline_query"),
                   switch_inline_query_current_chat=data.get("switch_inline_query_current_chat"))

    def to_dict(self) -> dict:
        data = {
            "text": self.text
        }

        if self.callback_data:
            data["callback_data"] = self.callback_data

        if self.url:
            data["url"] = self.url

        if self.switch_inline_query:
            data["switch_inline_query"] = self.switch_inline_query

        if self.switch_inline_query_current_chat:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat

        return data
