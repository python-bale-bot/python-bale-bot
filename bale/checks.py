#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.#  This software is licensed under the GNU General Public License v2.0.
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

import asyncio
import copy
import re
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Pattern, TypeVar

from ._message import Message

if TYPE_CHECKING:
    from bale import CallbackQuery
    from bale.context import Context

F = TypeVar("F", bound=Callable)
SelfT = TypeVar("SelfT")

__all__ = (
    "Check",
    "UPDATE",
    "MessageCheck",
    "MESSAGE",
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
    "PHOTO",
    "REPLY",
    "InvoicePayload",
    "SUCCESSFUL_PAYMENT",
    "STICKER",
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
    "CALLBACK_QUERY",
    "Data",
    "DATA",
    "ChatMemberCheck",
)


class Check:
    """
    Arguments:
        name:
            Name check for customization.

    Important:
        All sub-classes of this class must be an :class:`update <bale.Update>`.

    .. versionadded:: 3.0
    """

    __slots__ = ("name",)

    def __init__(self, name: str | None = None) -> None:
        self.name = name if name else self.__class__.__name__

    async def check_update(
        self, context: "Context"  # pylint: disable=unused-argument
    ) -> bool:
        """

        Arguments:
        update

        Returns
        -------

        """
        return True

    def __and__(self, other: "Check") -> "Check":
        """Combine this check with another using logical AND."""
        return _MergedCheck(self, and_check=other)

    def __or__(self, other: "Check") -> "Check":
        """Combine this check with another using logical OR."""
        return _MergedCheck(self, or_check=other)

    def __invert__(self) -> "Check":
        """Negate this check (logical NOT)."""
        return _InvertedCheck(self)

    def __xor__(self, other) -> "Check":
        """Combine this check with another using logical XOR."""
        return _ExclusiveCheck(self, other)

    def __repr__(self) -> str:
        return self.name


UPDATE = Check("Update")


class _MergedCheck(Check):
    __slots__ = ("base_check", "and_check", "or_check")

    def __init__(
        self,
        base_check: Check,
        and_check: Check | None = None,
        or_check: Check | None = None,
    ) -> None:
        super().__init__()
        if and_check and or_check:
            raise ValueError(
                "You cannot use both and_check and or_check simultaneously."
            )
        if not (and_check or or_check):
            raise ValueError(
                "You must enter one of the parameters and_check or or_check."
            )

        self.base_check = base_check
        self.and_check = and_check
        self.or_check = or_check

        self.name = f"MergedCheck[{'AND' if self.and_check else 'OR'}]({base_check}, {and_check or or_check})"

    async def check_update(self, context: "Context") -> bool:
        base_result = await self.base_check.check_update(context)

        if self.and_check and base_result:
            return await self.and_check.check_update(context)
        if self.or_check:
            return base_result or await self.or_check.check_update(context)

        return False


class _InvertedCheck(Check):
    __slots__ = ("base_check",)

    def __init__(self, base_check: Check) -> None:
        super().__init__()
        self.base_check = base_check

        self.name = f"InvertedCheck({base_check.name})"

    async def check_update(self, context: "Context") -> bool:
        return not await self.base_check.check_update(context)


class _ExclusiveCheck(Check):
    __slots__ = (
        "first_check",
        "second_check",
    )

    def __init__(self, first_check: Check, second_check: Check) -> None:
        super().__init__()

        self.first_check = first_check
        self.second_check = second_check

        self.name = f"ExclusiveCheck({first_check}, {second_check})"

    async def check_update(self, context: "Context") -> bool:
        first_check = await self.first_check.check_update(context)
        second_check = await self.second_check.check_update(context)

        return bool(first_check) ^ bool(second_check)


class MessageCheck(Check):
    """

    Arguments:
        name:
            Name check for customization.

    Important:
        All sub-classes of this class must have an :class:`update <bale.Update>` with a sent :attr:`~bale.Update.message`.

    .. versionadded:: 3.0
    """

    __slots__ = ("_extractor",)

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._extractor: (
            Callable[["Context"], "Message | Awaitable[Message | None] | None"] | None
        ) = None

    def target(
        self: SelfT,
        extractor: Callable[["Context"], "Message | Awaitable[Message | None] | None"],
    ) -> SelfT:
        new_check = copy.copy(self)
        new_check._extractor = extractor
        return new_check

    async def check_update(self, context: "Context") -> bool:
        update = context.update
        target_message = None
        if self._extractor:
            target_message = self._extractor(context)
            if asyncio.iscoroutine(target_message):
                target_message = await target_message
        elif update.message:
            target_message = update.message
        elif update.callback_query:
            target_message = update.callback_query.message
        elif update.edited_message:
            target_message = update.edited_message

        if (
            target_message
            and isinstance(target_message, Message)
            and await self.check(context, target_message)
        ):
            return True
        return False

    async def check(
        self, context: "Context", message: "Message"  # pylint: disable=unused-argument
    ) -> bool:
        return True


class _Message(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return message is not None


MESSAGE = MessageCheck("Message")


class MessageId(MessageCheck):
    __slots__ = ("message_id",)

    def __init__(self, message_id: int) -> None:
        super().__init__(name=f"MessageId({message_id})")
        self.message_id = message_id

    async def check(self, context: "Context", message: "Message") -> bool:
        return message.message_id == self.message_id


class _Animation(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.animation)


ANIMATION = _Animation("Animation")


class _Attachment(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.attachment)


ATTACHMENT = _Attachment("Attachment")


class _Audio(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.audio)


AUDIO = _Audio("Audio")


class _Video(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.video)


VIDEO = _Video("Video")


class _Contact(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.contact)


CONTACT = _Contact("Contact")


class _Document(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.document)


DOCUMENT = _Document("Document")


class _Voice(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.voice)


VOICE = _Voice("Voice")


class Content(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: list[str] | str | None = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__("Content" + (repr(strings) if strings else ""))
        self.strings = strings

    async def check(self, context: "Context", message: "Message") -> bool:
        if content := message.content:
            if not self.strings or content in self.strings:
                return True

        return False


CONTENT = Content()


class _Invoice(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.invoice)


INVOICE = _Invoice("Invoice")


class InvoicePayload(MessageCheck):
    __slots__ = ("pattern",)

    def __init__(self, pattern: str | Pattern[str]) -> None:
        super().__init__(name=f"InvoicePayload(pattern: {pattern})")
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern: Pattern[str] = pattern

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(
            message.invoice
            and self.pattern.match(message.invoice.invoice_payload or "")
        )


class _Location(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.location)


LOCATION = _Location("Location")


class _Photo(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.photo)


PHOTO = _Photo("Photo")


class _Reply(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.reply_to_message)


REPLY = _Reply("Reply")


class _SuccessfulPayment(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.successful_payment)


SUCCESSFUL_PAYMENT = _SuccessfulPayment("SuccessfulPayment")


class Text(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: list[str] | str | None = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__("Text" + (repr(strings) if strings else ""))
        self.strings = strings

    async def check(self, context: "Context", message: "Message") -> bool:
        if text := message.text:
            if not self.strings or text in self.strings:
                return True

        return False


TEXT = Text()


class _Command(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        if text := message.text:
            if (
                text.startswith("/")
                and text[1:].partition(" ")[0] in message.get_bot().get_commands()
            ):
                return True

        return False


class Caption(MessageCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: list[str] | str | None = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__("Caption" + (repr(strings) if strings else ""))
        self.strings = strings

    async def check(self, context: "Context", message: "Message") -> bool:
        if text := message.caption:
            if not self.strings or text in self.strings:
                return True

        return False


CAPTION = Caption()


class Chat(MessageCheck):
    __slots__ = ("chat_ids",)

    def __init__(self, chat_ids: list[int] | int | None = None) -> None:
        if isinstance(chat_ids, int):
            chat_ids = [chat_ids]
        if not chat_ids:
            chat_ids = []
        super().__init__("Chat" + (repr(chat_ids) if chat_ids else ""))
        self.chat_ids: list[int] = chat_ids

    async def check(self, context: "Context", message: "Message") -> bool:
        if chat := message.chat:
            if not (chat_ids := self.chat_ids):
                return True
            return chat.id in chat_ids

        return False


CHAT = Chat()


class Author(MessageCheck):
    __slots__ = ("user_ids",)

    def __init__(self, user_ids: list[int] | int | None = None) -> None:
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        if not user_ids:
            user_ids = []
        super().__init__("Author" + (repr(user_ids) if user_ids else ""))
        self.user_ids: list[int] = user_ids

    async def check(self, context: "Context", message: "Message") -> bool:
        if author := message.author:
            if not (user_ids := self.user_ids):
                return True
            return author.id in user_ids

        return False


AUTHOR = Author()


class _LeftChatMember(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.left_chat_member)


LEFT_CHAT_MEMBER = _LeftChatMember("LeftChatMember")


class _NewChatMembers(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.new_chat_members)


NEW_CHAT_MEMBERS = _NewChatMembers("NewChatMembers")


class _Sticker(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(message.sticker)


STICKER = _Sticker("Sticker")


class _Forward(MessageCheck):
    __slots__ = ()

    async def check(self, context: "Context", message: "Message") -> bool:
        return bool(
            message.forward_date
            or message.forward_from
            or message.forward_from_chat
            or message.forward_from_message_id
            or message.is_automatic_forward
        )


FORWARD = _Forward("Forward")


class ChatType:

    __slots__ = ()

    class _Private(MessageCheck):
        __slots__ = ()

        async def check(self, context: "Context", message: "Message") -> bool:
            return bool(message.chat and message.chat.is_private)

    PRIVATE = _Private("ChatType.Private")

    class _Group(MessageCheck):
        __slots__ = ()

        async def check(self, context: "Context", message: "Message") -> bool:
            return bool(message.chat and message.chat.is_group)

    GROUP = _Group("ChatType.Group")

    class _Channel(MessageCheck):
        __slots__ = ()

        async def check(self, context: "Context", message: "Message") -> bool:
            return bool(message.chat and message.chat.is_channel)

    CHANNEL = _Channel("ChatType.Channel")


class CallbackQueryCheck(Check):
    """
    Arguments:
        name:
            Name check for customization.

    Important:
        All sub-items of this check must have an :class:`update <bale.Update>` with a sent :attr:`callback query <bale.Update.callback_query>`.

    .. versionadded:: 3.0
    """

    __slots__ = ()

    async def check_update(self, context: "Context") -> bool:
        update = context.update
        target_callback_query: "CallbackQuery | None" = update.callback_query

        if target_callback_query and await self.check(context, target_callback_query):
            return True
        return False

    async def check(self, context: "Context", callback_query: "CallbackQuery") -> bool:
        return callback_query is not None


CALLBACK_QUERY = CallbackQueryCheck("CallbackQuery")


class Data(CallbackQueryCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: list[str] | str | None = None) -> None:
        if isinstance(strings, str):
            strings = [strings]
        super().__init__("Data" + (repr(strings) if strings else ""))
        self.strings = strings

    async def check(self, context: "Context", callback_query: "CallbackQuery") -> bool:
        if data := callback_query.data:
            if not self.strings or data in self.strings:
                return True

        return False


DATA = Data()


class ChatMemberCheck(Check):
    __slots__ = ("chat_ids",)

    def __init__(self, chat_ids: list[int] | int | None = None):
        if isinstance(chat_ids, int):
            chat_ids = [chat_ids]
        if not chat_ids:
            raise TypeError("At least one chat ID must be specified for ChatMember.")
        super().__init__("ChatMember" + repr(chat_ids))
        self.chat_ids: list[int] = chat_ids

    async def check_update(self, context: "Context") -> bool:
        update = context.update
        user = update.get_effective_user()
        bot = update.get_bot()

        if user:
            for cid in self.chat_ids:
                if await bot.get_chat_member(cid, user.id):
                    return True
        return False
