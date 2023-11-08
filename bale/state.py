"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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

    def store_message(self, message: "Message"):
        self._messages.appendleft(message)

    def store_chat(self, chat: "Chat"):
        self._chats[str(chat.chat_id)] = chat

    def store_user(self, user: "User"):
        self._users[str(user.chat_id)] = user

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