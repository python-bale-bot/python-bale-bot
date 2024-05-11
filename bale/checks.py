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

from typing import List, Union, Optional, Callable, TYPE_CHECKING
import inspect
if TYPE_CHECKING:
    from bale import Update, Message, CallbackQuery
    from typing_extensions import Self

__all__ = (
    "BaseCheck",
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
    "ChatType",
    "CallbackQueryCheck",
    "Data",
    "DATA"
)

class BaseCheck:
    __slots__ = ("name",)
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name if name else self.__class__.__name__

    async def check_update(self, update: "Update") -> bool:
        return True

    def __and__(self, other: "BaseCheck") -> "BaseCheck":
        return _MergedTwoCheck(self, and_check=other)

    def __or__(self, other: "BaseCheck") -> "BaseCheck":
        return _MergedTwoCheck(self, or_check=other)

    def __invert__(self) -> "BaseCheck":
        return _InvertedCheck(self)

    def __repr__(self) -> str:
        return self.name

class _MergedTwoCheck(BaseCheck):
    __slots__ = (
        "base_check",
        "and_check",
        "or_check"
    )
    def __init__(self, base_check: BaseCheck, and_check: Optional[BaseCheck] = None, or_check: Optional[BaseCheck] = None) -> None:
        super().__init__()
        if and_check and or_check:
            raise ValueError(
                "You can use and_check and or_check together"
            )

        self.base_check = base_check
        self.and_check = and_check
        self.or_check = or_check

        self.name = f"MergedCheck({base_check}, {and_check or or_check})"

    async def check_update(self, update: "Update") -> bool:
        base_check = await self.base_check.check_update(update)

        if self.and_check and base_check:
            return await self.and_check.check_update(update)
        elif self.or_check:
            return await self.or_check.check_update(update)

        return False

class _InvertedCheck(BaseCheck):
    __slots__ = ("base_check",)
    def __init__(self, base_check: BaseCheck) -> None:
        super().__init__()
        self.base_check = base_check

    async def check_update(self, update: "Update") -> bool:
        return not await self.base_check.check_update(update)

class MessageCheck(BaseCheck):
    __slots__ = ("__for_what",)
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.__for_what: Optional[Callable[[Update], Message]] = None

    @property
    def for_what(self) -> Callable[[Update], Message]:
        return self.__for_what

    @for_what.setter
    def for_what(self, value: Callable[[Update], Message]) -> None:
        self.set_for_what(value)

    def set_for_what(self, value: Callable[[Update], Message]) -> "Self":
        if not inspect.isfunction(value):
            raise TypeError(
                "for_what param must be a function"
            )

        self.__for_what = value
        return self

    async def check_update(self, update: "Update") -> bool:
        target_message: Optional[Message] = None
        if self.for_what and (result := self.for_what(update)):
            if isinstance(result, Message):
                target_message = self.for_what(update)
        else:
            if update.message:
                target_message = update.message
            elif update.callback_query:
                target_message = update.callback_query.message
            elif update.edited_message:
                target_message = update.edited_message

        if target_message and await self.check(target_message):
            return True
        return False

    async def check(self, message: Message) -> bool:
        return message is not None

class _Message(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return message is not None

class MessageId(MessageCheck):
    __slots__ = ("message_id",)

    def __init__(self, message_id: int) -> None:
        super().__init__(name=f"MessageId({message_id})")
        self.message_id = message_id

    async def check(self, message: Message) -> bool:
        return message.message_id == self.message_id

class _Animation(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.animation)


ANIMATION = _Animation("Animation")

class _Attachment(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.attachment)


ATTACHMENT = _Attachment("Attachment")

class _Audio(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.audio)


AUDIO = _Audio("Audio")

class _Video(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.video)


VIDEO = _Video("Video")

class _Contact(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.contact)


CONTACT = _Contact("Contact")

class _Document(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.document)


DOCUMENT = _Document("Document")

class _Voice(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
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

    async def check(self, message: Message) -> bool:
        if content := message.content:
            if not self.strings or content in self.strings:
                return True

        return False


CONTENT = Content()

class _Invoice(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.invoice)


INVOICE = _Invoice("Invoice")

class _Location(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.location)


LOCATION = _Location("Location")

class _Photos(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
        return bool(message.photos)


PHOTOS = _Photos("Photos")

class _Reply(MessageCheck):
    __slots__ = ()

    def check(self, message: Message):
        return bool(message.reply_to_message)


REPLY = _Reply("Reply")

class _SuccessfulPayment(MessageCheck):
    __slots__ = ()

    async def check(self, message: Message) -> bool:
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

    async def check(self, message: Message) -> bool:
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

    async def check(self, message: Message) -> bool:
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

    async def check(self, message: Message) -> bool:
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

    async def check(self, message: Message) -> bool:
        if author := message.from_user:
            return author.id in self.chat_ids
        return False


AUTHOR = Author()

class _LeftChatMember(MessageCheck):
    __slots__ = ()
    async def check(self, message: Message) -> bool:
        return bool(message.left_chat_member)


LEFT_CHAT_MEMBER = _LeftChatMember("LeftChatMember")

class _NewChatMembers(MessageCheck):
    __slots__ = ()
    async def check(self, message: Message) -> bool:
        return bool(message.new_chat_members)


NEW_CHAT_MEMBERS = _NewChatMembers("NewChatMembers")

class _Sticker(MessageCheck):
    __slots__ = ()
    async def check(self, message: Message) -> bool:
        return bool(message.sticker)


STICKER = _Sticker("Sticker")

class ChatType:
    __slots__ = ()

    class _Private(MessageCheck):
        __slots__ = ()

        async def check(self, message: Message) -> bool:
            return message.chat.is_private_chat

    PRIVATE = _Private("ChatType.Private")

    class _Group(MessageCheck):
        __slots__ = ()

        async def check(self, message: Message) -> bool:
            return message.chat.is_group_chat

    GROUP = _Group("ChatType.Group")

    class _Channel(MessageCheck):
        __slots__ = ()

        async def check(self, message: Message) -> bool:
            return message.chat.is_channel_chat

    CHANNEL = _Channel("ChatType.Channel")

class CallbackQueryCheck(BaseCheck):
    __slots__ = ("for_what",)
    async def check_update(self, update: "Update") -> bool:
        target_callback_query: Optional[CallbackQuery] = update.callback_query

        if target_callback_query and await self.check(target_callback_query):
            return True
        return False

    async def check(self, callback_query: CallbackQuery) -> bool:
        return callback_query is not None


class Data(CallbackQueryCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: Optional[Union[List[str], str]] = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__(
            "Data" + (
                repr(strings) if strings else ""
            )
        )
        self.strings = strings

    async def check(self, callback_query: CallbackQuery) -> bool:
        if data := callback_query.data:
            if not self.strings or data in self.strings:
                return True

        return False


DATA = Data()