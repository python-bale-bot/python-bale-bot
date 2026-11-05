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

from datetime import datetime
from typing import TYPE_CHECKING, TypeAlias

from ._baleobject import BaleObject
from ._chat import Chat
from ._invoice import Invoice
from ._messageentity import MessageEntity
from ._poll import Poll
from ._sticker import Sticker
from ._successfulpayment import SuccessfulPayment
from ._ui import InlineKeyboardMarkup, ReplyKeyboardMarkup
from ._user import User
from ._utils.entity import extract_entity_text
from ._utils.typehint import MISSING, FileInput, SentinelOrValue
from ._webappdata import WebAppData
from .attachments import (Animation, Audio, Contact, Document, Location,
                          MediaInput, PhotoSize, Video, Voice)
from .helpers import parse_time

if TYPE_CHECKING:
    from bale import ReplyKeyboardRemove

    from ._types.message import Message as MessagePayload

    ReplyMarkupT: TypeAlias = (
        "InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove"
    )


class Message(BaleObject):
    """This object represents a message in the Bale messenger.

    Equality conditions:
        1. The second object must be an instance of :class:`Message`.
        2. Both the unique message identifier (:attr:`message_id`) and the unique identifier of the chat :attr:`chat_id` in which the message was sent must be equal. It should be noted that if in the equality comparison of two message instances, even one of them lacks the chat property, the truth value will depend solely on the equality of the unique message identifiers.


    Attributes:
        message_id (:obj:`str`):
            Unique message identifier inside this chat.

            Note:
                It should be noted that this property returns ``0`` for system-related messages (such as member addition).
        date (:class:`datetime.datetime`):
            The time when the message was sent, represented as a Unix timestamp and converted to a Python datetime object.
        chat (:class:`~bale.Chat`, optional):
            The conversation in which the message was sent.
        from_user (:class:`~bale.User`, optional):
            The user who sent the message. For messages sent on behalf of a channel, this field represents the channel.

            Important:
                ``from_user`` corresponds to ``from`` in the Bale documentation. Since ``from`` is a reserved keyword in Python, ``from_user`` is used instead.
        text (:obj:`str`, optional):
            The text of the message.
        caption (:obj:`str`, optional):
            The caption of the message. This field is used for media messages.
        entities (list of :class:`~bale.MessageEntity`, optional):
            A list of special entities in the message text.

            .. versionadded:: 3.0
        caption_entities (list of :class:`~bale.MessageEntity`, optional):
            A list of special entities in the message caption.

            .. versionadded:: 3.0
        photo (list of :class:`~bale.PhotoSize`, optional):
            Information about the photo or photos included in the message.
        document (:class:`~bale.Document`, optional):
            Information about the file included in the message.
        video (:class:`~bale.Video`, optional):
            Information about the video included in the message.
        audio (:class:`~bale.Audio`, optional):
            Information about the audio file included in the message.
        voice (:class:`~bale.Voice`, optional):
            Information about the voice message included in the message.
        animation (:class:`~bale.Animation`, optional):
            Information about the animated media (GIF) included in the message.
        sticker (:class:`~bale.Sticker`, optional):
            Information about the sticker included in the message.
        poll (:class:`~bale.Poll`, optional):
            Information about the poll included in the message.

            .. versionadded:: 3.0
        contact (:class:`~bale.Contact`, optional):
            Information about the contact shared in the message.
        location (:class:`~bale.Location`, optional):
            Information about the location shared in the message.
        invoice (:class:`~bale.Invoice`, optional):
            Information about the payment request included in the message.
        successful_payment (:class:`~bale.SuccessfulPayment`, optional):
            Information about the successful payment indicated by the message. This field is sent only to the bot and is not visible to other users.
        web_app_data (:class:`~bale.WebAppData`, optional):
            Information sent by a mini app. This field is sent only to the bot and is not visible to other users.

            .. versionadded:: 3.0
        reply_to_message (:class:`~bale.Message`, optional):
            The message to which this message is a reply. To prevent unwanted circular references, this field is not populated if the replied-to message is itself a reply to another message.
        reply_markup (:class:`~bale.InlineKeyboardMarkup`, optional):
            The inline keyboard attached to the message.

            .. versionadded:: 3.0
        message_thread_id (:obj:`int`, optional):
            The identifier of the message thread. This field is populated only in discussion groups.

            .. versionadded:: 3.0
        media_group_id (:obj:`str`, optional):
            The unique identifier of the media group. All messages belonging to the same media group have the same value.

            .. versionadded:: 3.0
        forward_from (:class:`~bale.User`, optional):
            The original sender of the message, if the message was forwarded.
        forward_from_chat (:class:`~bale.Chat`, optional):
            The original chat from which the message was forwarded.
        forward_from_message_id (:class:`int`, optional):
            The identifier of the original forwarded message within :attr:`forward_from_chat`.
        forward_date (:class:`datetime.datetime`, optional):
            The time when the original message was sent, if the message was forwarded. The value is represented as a Unix timestamp and converted to a Python :class:`datetime.datetime` object
        is_automatic_forward (:obj:`bool`, optional):
            Indicates whether the message was automatically forwarded from a channel to its linked discussion group.

            .. versionadded:: 3.0
        edit_date (:class:`datetime.datetime`, optional):
            The time when the message was last edited, represented as a Unix timestamp and converted to a Python :class:`datetime.datetime` object.
        new_chat_members (list of :class:`~bale.User`, optional):
            Information about the user or users who were added to the chat. This field may contain the bot itself.
        left_chat_member (:class:`~bale.User`, optional):
            Information about the user who left the chat. This field may contain the bot itself.
    """

    __slots__ = (
        "message_id",
        "date",
        "chat",
        "from_user",
        "text",
        "caption",
        "entities",
        "caption_entities",
        "photo",
        "document",
        "video",
        "audio",
        "voice",
        "animation",
        "sticker",
        "poll",
        "contact",
        "location",
        "invoice",
        "successful_payment",
        "web_app_data",
        "reply_to_message",
        "reply_markup",
        "message_thread_id",
        "media_group_id",
        "forward_from",
        "forward_from_chat",
        "forward_from_message_id",
        "forward_date",
        "is_automatic_forward",
        "edit_date",
        "new_chat_members",
        "left_chat_member",
    )

    def __init__(
        self,
        message_id: int,
        date: datetime,
        chat: "Chat | None" = None,
        from_user: "User | None" = None,
        text: str | None = None,
        caption: str | None = None,
        entities: list["MessageEntity"] | None = None,
        caption_entities: list["MessageEntity"] | None = None,
        photo: list["PhotoSize"] | None = None,
        document: "Document | None" = None,
        video: "Video | None" = None,
        audio: "Audio | None" = None,
        voice: "Voice | None" = None,
        animation: "Animation | None" = None,
        sticker: "Sticker | None" = None,
        poll: "Poll | None" = None,
        contact: "Contact | None" = None,
        location: "Location | None" = None,
        invoice: "Invoice | None" = None,
        successful_payment: "SuccessfulPayment | None" = None,
        web_app_data: "WebAppData | None" = None,
        reply_to_message: "Message | None" = None,
        reply_markup: "InlineKeyboardMarkup | None" = None,
        message_thread_id: int | None = None,
        media_group_id: str | None = None,
        forward_from: "User | None" = None,
        forward_from_chat: "Chat | None" = None,
        forward_from_message_id: int | None = None,
        forward_date: datetime | None = None,
        is_automatic_forward: bool | None = None,
        edit_date: datetime | None = None,
        new_chat_members: list["User"] | None = None,
        left_chat_member: "User | None" = None,
    ):
        super().__init__()
        self._id: int = message_id
        self.message_id = message_id
        self.date = date

        self.chat = chat
        self.from_user = from_user

        self.text = text
        self.caption = caption
        self.entities = entities
        self.caption_entities = caption_entities

        self.photo = photo
        self.document = document
        self.video = video
        self.audio = audio
        self.voice = voice
        self.animation = animation
        self.sticker = sticker

        self.poll = poll
        self.contact = contact
        self.location = location
        self.invoice = invoice
        self.successful_payment = successful_payment
        self.web_app_data = web_app_data

        self.reply_to_message = reply_to_message
        self.reply_markup = reply_markup
        self.message_thread_id = message_thread_id
        self.media_group_id = media_group_id

        self.forward_from = forward_from
        self.forward_from_chat = forward_from_chat
        self.forward_from_message_id = forward_from_message_id
        self.forward_date = forward_date
        self.is_automatic_forward = is_automatic_forward

        self.edit_date = edit_date
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member

        self._lock()

    @property
    def id(self) -> int:
        """An alias for :attr:`message_id`"""
        return self.message_id

    @property
    def author(self) -> "User | None":
        """An alias for :attr:`from_user`"""
        return self.from_user

    @property
    def attachment(
        self,
    ) -> "Audio | Document | PhotoSize | Video | Animation | Voice | None":
        """The attachment included in the message, if any. This may be a video, photo, audio file, animation, voice message, or document. If the message contains multiple photos, the last photo is returned."""
        attachment = (
            self.video
            or self.photo
            or self.audio
            or self.animation
            or self.voice
            or self.document
        )
        if isinstance(attachment, list):
            return attachment[-1] if len(attachment) > 0 else None

        return attachment

    @property
    def content(self) -> str | None:
        """The textual content of the message. either its text or its caption."""
        return self.text or self.caption

    @property
    def chat_id(self) -> str | int | None:
        """The unique identifier of the chat in which the message was sent. Returns :obj:`None` if the message has no chat."""
        if self.chat:
            return self.chat.id
        return None

    @property
    def reply_to_message_id(self) -> int | None:
        """The identifier of the message to which this message is a reply. Returns :obj:`None` if this message is not a reply."""
        if self.reply_to_message:
            return self.reply_to_message.id
        return None

    def _fetch_chat_id(self) -> str | int:
        maybe_chat = self.chat
        if not maybe_chat:
            raise RuntimeError(
                "Missing required value: 'chat'. "
                "Make sure 'chat' is properly initialized before using it."
            )

        return maybe_chat.id

    @staticmethod
    def _parse_entities(
        text: str | None = None,
        entities: list["MessageEntity"] | None = None,
        types: list[str] | set[str] | str | None = None,
    ) -> dict["MessageEntity", str]:
        if isinstance(types, str):
            types = {types}
        elif types is not None:
            types = set(types)

        if text and entities:
            res = {
                entity: extract_entity_text(text, entity=entity)
                for entity in entities
                if not types or entity.type in types  # (p -> q) <=> (~p v q)
            }
            return res

        return {}

    def parse_entities(
        self, types: list[str] | set[str] | str | None = None
    ) -> dict["MessageEntity", str]:
        return self._parse_entities(self.text, self.entities, types)

    def parse_caption_entities(
        self, types: list[str] | set[str] | str | None = None
    ) -> dict["MessageEntity", str]:
        return self._parse_entities(self.caption, self.caption_entities, types)

    @classmethod
    def from_dict(cls, data: "MessagePayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaleObject.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["date"] = parse_time(parsed_data.get("date"))

        parsed_data["chat"] = Chat.from_dict(parsed_data.get("chat"), bot)
        parsed_data["from_user"] = User.from_dict(parsed_data.pop("from", None), bot)

        parsed_data["entities"] = MessageEntity.from_list(
            parsed_data.get("entities"), bot
        )
        parsed_data["caption_entities"] = MessageEntity.from_list(
            parsed_data.get("caption_entities"), bot
        )

        parsed_data["photo"] = PhotoSize.from_list(parsed_data.pop("photo", None), bot)
        parsed_data["document"] = Document.from_dict(parsed_data.get("document"), bot)
        parsed_data["video"] = Video.from_dict(parsed_data.get("video"), bot)
        parsed_data["audio"] = Audio.from_dict(parsed_data.get("audio"), bot)
        parsed_data["voice"] = Voice.from_dict(parsed_data.get("voice"), bot)
        parsed_data["animation"] = Animation.from_dict(
            parsed_data.get("animation"), bot
        )
        parsed_data["sticker"] = Sticker.from_dict(parsed_data.get("sticker"), bot)

        parsed_data["poll"] = Poll.from_dict(parsed_data.get("poll"), bot)
        parsed_data["contact"] = Contact.from_dict(parsed_data.get("contact"), bot)
        parsed_data["location"] = Location.from_dict(parsed_data.get("location"), bot)
        parsed_data["invoice"] = Invoice.from_dict(parsed_data.get("invoice"), bot)
        parsed_data["successful_payment"] = SuccessfulPayment.from_dict(
            parsed_data.get("successful_payment"), bot
        )
        parsed_data["web_app_data"] = WebAppData.from_dict(
            parsed_data.get("web_app_data"), bot
        )

        parsed_data["reply_to_message"] = Message.from_dict(
            parsed_data.get("reply_to_message"), bot
        )
        parsed_data["reply_markup"] = InlineKeyboardMarkup.from_dict(
            parsed_data.get("reply_markup"), bot
        )

        parsed_data["forward_from"] = User.from_dict(
            parsed_data.get("forward_from"), bot
        )
        parsed_data["forward_from_chat"] = Chat.from_dict(
            parsed_data.get("forward_from_chat"), bot
        )
        parsed_data["forward_date"] = parse_time(parsed_data.get("forward_date"))

        parsed_data["edit_date"] = parse_time(parsed_data.pop("edit_date", None))
        parsed_data["new_chat_members"] = User.from_list(
            parsed_data.get("new_chat_members"), bot
        )
        parsed_data["left_chat_member"] = User.from_dict(
            parsed_data.get("left_chat_member"), bot
        )

        return super().from_dict(parsed_data, bot)

    async def reply(
        self,
        text: str,
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply("Hi, python-bale-bot!")
        """
        return await self.get_bot().send_message(
            self._fetch_chat_id(),
            text,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            **kwargs,
        )

    async def forward(self, chat_id: str | int, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.forward(6429983203)
        """
        return await self.get_bot().forward_message(
            chat_id, self._fetch_chat_id(), self.message_id, **kwargs
        )

    async def reply_document(
        self,
        document: "Document | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                with open('./my_file.pdf', 'rb') as f:
                    await message.reply_document(f.read(), caption='Bale Bot API Description', file_name='bale-bot-api.pdf')
        """
        return await self.get_bot().send_document(
            self._fetch_chat_id(),
            document,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_photo(
        self,
        photo: "PhotoSize | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                with open('./my_file.png', 'rb') as f:
                    await message.reply_photo(f.read(), caption='Bale image', file_name='bale.png')
        """
        return await self.get_bot().send_photo(
            self._fetch_chat_id(),
            photo,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_sticker(self, sticker: "Sticker | FileInput", **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                    await message.reply_sticker(sticker)
        """
        return await self.get_bot().send_sticker(
            self._fetch_chat_id(),
            sticker,
            reply_to_message_id=self.message_id,
            **kwargs,
        )

    async def reply_video(
        self,
        video: "Video | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_video("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_video(
            self._fetch_chat_id(),
            video,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_animation(
        self,
        animation: "Animation | FileInput",
        *,
        duration: SentinelOrValue[int] = MISSING,
        width: SentinelOrValue[int] = MISSING,
        height: SentinelOrValue[int] = MISSING,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_animation("FILE_ID", caption = "this is a caption", *args, **kwargs)
        """
        return await self.get_bot().send_animation(
            self._fetch_chat_id(),
            animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_audio(
        self,
        audio: "Audio | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_audio("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_audio(
            self._fetch_chat_id(),
            audio,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_voice(
        self,
        voice: "Voice | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_voice("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_voice(
            self._fetch_chat_id(),
            voice,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            file_name=file_name,
            **kwargs,
        )

    async def reply_location(
        self,
        location: "Location",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(
            self._fetch_chat_id(),
            location,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            **kwargs,
        )

    async def reply_contact(
        self,
        contact: "Contact",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_contact(bale.Contact('09****', 'first name', 'last name'))
        """
        return await self.get_bot().send_contact(
            self._fetch_chat_id(),
            contact,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
            **kwargs,
        )

    async def reply_media_group(
        self,
        media: list["MediaInput"],
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.reply_media_group([
                    InputMediaPhoto("File ID", caption="example caption"),
                    InputMediaPhoto("File ID"),
                    InputMediaPhoto("File ID")
                ], ...)
        """
        return await self.get_bot().send_media_group(
            self._fetch_chat_id(),
            media,
            reply_markup=reply_markup,
            reply_to_message_id=self.id,
            **kwargs,
        )

    async def copy(
        self,
        chat_id: int | str,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        Hint:

            .. code-block:: python

                await message.copy(
                    6429983203, *args, **kwargs
                )
        """
        return await self.get_bot().copy_message(
            chat_id,
            self._fetch_chat_id(),
            self.id,
            reply_to_message_id=reply_to_message_id,
            **kwargs,
        )

    async def edit_text(
        self,
        text: str,
        *,
        reply_markup: SentinelOrValue["InlineKeyboardMarkup"] = MISSING,
        **kwargs,
    ) -> Message:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.edit("Bye!")
        """
        return await self.get_bot().edit_message_text(
            self._fetch_chat_id(),
            self.message_id,
            text,
            reply_markup=reply_markup,
            **kwargs,
        )

    async def edit_caption(
        self,
        caption: str,
        *,
        reply_markup: SentinelOrValue["InlineKeyboardMarkup"] = MISSING,
        **kwargs,
    ) -> Message:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.edit_caption("Edited!")
        """
        return await self.get_bot().edit_message_caption(
            self._fetch_chat_id(),
            self.message_id,
            caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    async def edit_reply_markup(
        self, reply_markup: "InlineKeyboardMarkup", **kwargs
    ) -> Message:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.edit_reply_markup(None)
        """
        return await self.get_bot().edit_message_reply_markup(
            self._fetch_chat_id(), self.message_id, reply_markup=reply_markup, **kwargs
        )

    async def delete(self, *, delay: int | float | None = None, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await message.delete(delay=5)
        """
        return await self.get_bot().delete_message(
            self._fetch_chat_id(), self.message_id, delay=delay, **kwargs
        )

    def __eq__(self, other: object) -> bool:
        """
        :meta private:
        """
        if isinstance(other, Message):
            if self.chat_id is not None and other.chat_id is not None:
                if self.chat_id != other.chat_id:
                    return False
            return self._id == other._id

        return False
