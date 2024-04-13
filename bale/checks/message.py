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

from typing import Optional, List, Union, Callable
import inspect
from bale import Message, Update
from .basecheck import BaseCheck

__all__ = (
    "MessageCheck",
    "MessageId",
    "ANIMATION",
    "ATTACHMENT",
    "AUDIO",
    "VIDEO",
    "CONTACT",
    "DOCUMENT",
    "VOICE",
    "Content",
    "CONTENT",
    "INVOICE",
    "LOCATION",
    "PHOTOS",
    "REPLY",
    "SUCCESSFUL_PAYMENT",
    "Text",
    "TEXT",
    "Caption",
    "CAPTION",
    "Chat",
    "CHAT",
    "Author",
    "AUTHOR",
    "LEFT_CHAT_MEMBER",
    "NEW_CHAT_MEMBERS",
    "ChatType"
)

# TODO: COMPLETE DOCS

class MessageCheck(BaseCheck):
    __slots__ = ("for_what",)
    def __init__(self, name: Optional[str] = None, for_what: Optional[Callable[[Update], Message]] = None):
        super().__init__(name)
        if for_what and not inspect.isfunction(for_what):
            raise TypeError(
                "for_what param must be a function"
            )

        self.for_what: Optional[Callable[[Update], Message]] = for_what

    def check_update(self, update: "Update") -> bool:
        target_message: Optional[Message] = None
        if self.for_what:
            target_message = self.for_what(update)
        else:
            if update.message:
                target_message = update.message
            elif update.callback_query:
                target_message = update.callback_query.message
            elif update.edited_message:
                target_message = update.edited_message

        if target_message and self.check(target_message):
            return True
        return False

    def check(self, message: Message) -> bool:
        return message is not None

class _Message(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return message is not None

class MessageId(MessageCheck):
    __slots__ = ("message_id",)

    def __init__(self, message_id: int):
        super().__init__(name=f"MessageId({message_id})")
        self.message_id = message_id

    def check(self, message: Message) -> bool:
        return message.message_id == self.message_id

class _Animation(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.animation)


ANIMATION = _Animation("Animation")

class _Attachment(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.attachment)


ATTACHMENT = _Attachment("Attachment")

class _Audio(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.audio)


AUDIO = _Audio("Audio")

class _Video(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.video)


VIDEO = _Video("Video")

class _Contact(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.contact)


CONTACT = _Contact("Contact")

class _Document(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.document)


DOCUMENT = _Document("Document")

class _Voice(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.voice)


VOICE = _Voice("Voice")

class Content(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: Optional[Union[List[str], str]] = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__(
            "Content" + (
                repr(strings) if strings else ""
            )
        )
        self.strings = strings

    def check(self, message: Message) -> bool:
        if content := message.content:
            if not self.strings or content in self.strings:
                return True

        return False


CONTENT = Content()

class _Invoice(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.invoice)


INVOICE = _Invoice("Invoice")

class _Location(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.location)


LOCATION = _Location("Location")

class _Photos(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.photos)


PHOTOS = _Photos("Photos")

class _Reply(MessageCheck):
    __slots__ = ()

    def check(self, message: Message):
        return bool(message.reply_to_message)


REPLY = _Reply("Reply")

class _SuccessfulPayment(MessageCheck):
    __slots__ = ()

    def check(self, message: Message) -> bool:
        return bool(message.successful_payment)


SUCCESSFUL_PAYMENT = _SuccessfulPayment("SuccessfulPayment")

class Text(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: Optional[Union[List[str], str]] = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__(
            "Text" + (
                repr(strings) if strings else ""
            )
        )
        self.strings = strings

    def check(self, message: Message) -> bool:
        if text := message.text:
            if not self.strings or text in self.strings:
                return True

        return False


TEXT = Text()

class Caption(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: Optional[Union[List[str], str]] = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__(
            "Caption" + (
                repr(strings) if strings else ""
            )
        )
        self.strings = strings

    def check(self, message: Message) -> bool:
        if text := message.caption:
            if not self.strings or text in self.strings:
                return True

        return False


CAPTION = Caption()

class Chat(MessageCheck):
    __slots__ = ("chat_ids",)

    def __init__(self, chat_ids: Optional[Union[int, List[int]]] = None) -> None:
        super().__init__()
        if isinstance(chat_ids, int):
            self.chat_ids = [chat_ids]
        self.chat_ids = chat_ids

    def check(self, message: Message) -> bool:
        if chat := message.chat:
            return chat.id in self.chat_ids
        return False


CHAT = Chat()

class Author(MessageCheck):
    __slots__ = ("chat_ids",)

    def __init__(self, chat_ids: Optional[Union[int, List[int]]] = None) -> None:
        super().__init__()
        if isinstance(chat_ids, int):
            self.chat_ids = [chat_ids]
        self.chat_ids = chat_ids

    def check(self, message: Message) -> bool:
        if author := message.from_user:
            return author.id in self.chat_ids
        return False


AUTHOR = Author()

class _LeftChatMember(MessageCheck):
    __slots__ = ()
    def check(self, message: Message) -> bool:
        return bool(message.left_chat_member)


LEFT_CHAT_MEMBER = _LeftChatMember("LeftChatMember")

class _NewChatMembers(MessageCheck):
    __slots__ = ()
    def check(self, message: Message) -> bool:
        return bool(message.new_chat_members)


NEW_CHAT_MEMBERS = _NewChatMembers("NewChatMembers")

class _Sticker(MessageCheck):
    __slots__ = ()
    def check(self, message: Message) -> bool:
        return bool(message.sticker)


STICKER = _Sticker("Sticker")

class ChatType:
    __slots__ = ()

    class _Private(MessageCheck):
        __slots__ = ()

        def check(self, message: Message) -> bool:
            return message.chat.is_private_chat

    PRIVATE = _Private("ChatType.Private")

    class _Group(MessageCheck):
        __slots__ = ()

        def check(self, message: Message) -> bool:
            return message.chat.is_group_chat

    GROUP = _Group("ChatType.Group")

    class _Channel(MessageCheck):
        __slots__ = ()

        def check(self, message: Message) -> bool:
            return message.chat.is_channel_chat

    CHANNEL = _Channel("ChatType.Channel")
