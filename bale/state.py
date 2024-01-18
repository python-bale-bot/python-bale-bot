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
from typing import TYPE_CHECKING, Deque, Optional, Union
import weakref
from collections import deque
from bale.helpers import find
if TYPE_CHECKING:
    from bale import Bot, Message, User, Chat

__all__ = (
    "State",
)

class State:
    __slots__ = (
        "_bot",
        "_messages",
        "_users",
        "_chats",
        "_cash_max_size"
    )

    def __init__(self, bot: "Bot", **kwargs):
        self._bot: "Bot" = bot
        self._cash_max_size: int = kwargs.get('max_messages', 1000)
        self._messages: Deque["Message"] = deque(maxlen=self._cash_max_size)
        self._users: weakref.WeakValueDictionary[str, User] = weakref.WeakValueDictionary()
        self._chats: weakref.WeakValueDictionary[str, Chat] = weakref.WeakValueDictionary()

    @property
    def bot(self) -> "Bot":
        return self._bot

    @property
    def messages(self) -> Deque["Message"]:
        return self._messages

    @property
    def users(self) -> weakref.WeakValueDictionary[str, "User"]:
        return self._users

    @property
    def chats(self) -> weakref.WeakValueDictionary[str, "Chat"]:
        return self._chats

    def store_message(self, message: "Message"):
        self._messages.appendleft(message)

    def store_chat(self, chat: "Chat"):
        self._chats[str(chat.id)] = chat

    def store_user(self, user: "User"):
        self._users[str(user.chat_id)] = user

    def update_message(self, message: "Message"):
        for index, msg in enumerate(self._messages):
            if msg.message_id == message.message_id and msg.chat_id == message.chat_id:
                self._messages[index] = message
                break

    def get_message(self, chat_id, message_id: int) -> Optional["Message"]:
        for msg in self._messages:
            if msg.message_id == message_id and msg.chat_id == chat_id:
                return msg

        return None

    def get_chat(self, chat_id: Union[str, int]) -> Optional["Chat"]:
        return self._chats.get(str(chat_id))

    def get_user(self, user_id) -> Optional["User"]:
        return self._users.get(str(user_id))

    def get_all_users(self):
        for user in self._users:
            yield user

    def remove_message(self, message_id: Union[str, int], chat_id: Union[str, int]):
        message = find(lambda m: m.message_id == str(message_id) and m.chat_id == str(chat_id), self._messages)
        if message:
            self._messages.remove(message)

    def remove_chat(self, chat_id: Union[str, int]):
        if self._chats.get(str(chat_id)):
            del self._chats[str(chat_id)]

    def remove_user(self, user_id: Union[str, int]):
        if self._users.get(str(user_id)):
            del self._users[str(user_id)]