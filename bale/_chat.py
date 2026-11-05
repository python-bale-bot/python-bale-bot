# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, TypeVar

from ._baleobject import BaleObject
from ._user import User
from ._utils.context_manager import ChatActionContextManager
from ._utils.typehint import MISSING, SentinelOrValue
from .constants import ChatType

if TYPE_CHECKING:
    from pathlib import Path

    from bale import (Animation, Audio, Contact, Document,
                      InlineKeyboardMarkup, InputFile, InputMediaAnimation,
                      InputMediaAudio, InputMediaDocument, InputMediaPhoto,
                      InputMediaVideo, LabeledPrice, Location, Message,
                      PhotoSize, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Sticker, Video, Voice)

    ReplyMarkupT: TypeAlias = (
        "InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove"
    )
    FileInput: TypeAlias = str | bytes | Path | InputFile
    MediaInput: TypeAlias = (
        InputMediaPhoto
        | InputMediaVideo
        | InputMediaAnimation
        | InputMediaAudio
        | InputMediaDocument
    )

ChatT = TypeVar("ChatT", bound="Chat")

__all__ = ("Chat",)


class Chat(BaleObject):
    """This object represents basic information about a chat in `Bale <https://ble.ir>`_. It can be a private chat, a group, or a channel.

    Equality conditions:
        1. The second object must be an instance of :class:`bale.Chat`. It can also be :class:`~bale.ChatFullInfo`.
        2. The unique identifier of the chat must be equal.

    Attributes:
        id (:class:`int`):
            Unique identifier for this chat.
        type (:class:`str`):
            Type of chat, can be either ``private``, ``group``, or ``channel``.
        title (:class:`str`, optional):
            Title, for supergroups, groups and channel chats.
        username (:class:`str`, optional):
            Username, for private chats, supergroups, groups and channels if available.
        first_name (:class:`str`, optional):
            First name of the other party in a private chat.
        last_name (:class:`str`, optional):
            Last name of the other party in a private chat.

    .. versionchanged:: 3.0
        Additional fields previously added to this object exclusively via the :meth:`~bale.Bot.get_chat` method have been moved to the :class:`~bale.ChatFullInfo` class.
    """

    __slots__ = (
        "id",
        "type",
        "title",
        "username",
        "first_name",
        "last_name",
        "bot",
    )

    def __init__(
        self,
        id: int,
        type: str,
        title: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> None:
        super().__init__()
        self._id = id
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

        self._lock()

    @property
    def mention(self) -> str | None:
        """:obj:`str`, optional: mention chat with username, for groups and channels if available."""
        if self.username:
            return "@" + self.username

        return None

    @property
    def is_private(self) -> bool:
        """:obj:`bool`: If the chat is private, :obj:`True` will be returned."""
        return self.type == ChatType.PRIVATE

    @property
    def is_group(self) -> bool:
        """:obj:`bool`: If the chat is group, :obj:`True` will be returned."""
        return self.type == ChatType.GROUP

    @property
    def is_channel(self) -> bool:
        """:obj:`bool`: If the chat is channel, :obj:`True` will be returned."""
        return self.type == ChatType.CHANNEL

    @property
    def full_name(self) -> str:
        full = self.first_name or ""
        if last_name := self.last_name:
            full += f" {last_name}"

        return full

    async def send(
        self,
        text: str,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        Arguments:
            text:
                Text of the message to be sent. Max 4096 characters after entities parsing.
            reply_markup:
                |reply_markup|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.send("hi, python-bale-bot!")
        """
        return await self.get_bot().send_message(
            self.id, text, reply_markup=reply_markup, **kwargs
        )

    async def send_document(
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

                await chat.send_document("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_document(
            self.id,
            document,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_photo(
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

                await chat.send_photo("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_photo(
            self.id,
            photo,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_video(
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

                await chat.send_video("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_video(
            self.id,
            video,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_animation(
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

                await chat.send_animation("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_animation(
            self.id,
            animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_audio(
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

                await chat.send_audio("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_audio(
            self.id,
            audio,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_voice(
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

                await chat.send_voice("FILE_ID", caption = "this is caption", ...)
        """
        return await self.get_bot().send_voice(
            self.id,
            voice,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
            **kwargs,
        )

    async def send_location(self, location: "Location", **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale import Location
                await chat.send_location(Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(self.id, location, **kwargs)

    async def send_contact(self, contact: "Contact", **kwargs) -> "Message":
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale import Contact
                await chat.send_contact(Contact('09123456789', 'Ali Irani'))
        """
        return await self.get_bot().send_contact(self.id, contact, **kwargs)

    async def send_invoice(
        self,
        title: str,
        description: str,
        provider_token: str,
        prices: list["LabeledPrice"],
        *,
        invoice_payload: SentinelOrValue[str] = MISSING,
        photo_url: SentinelOrValue[str] = MISSING,
        need_name: SentinelOrValue[bool] = MISSING,
        need_phone_number: SentinelOrValue[bool] = MISSING,
        need_email: SentinelOrValue[bool] = MISSING,
        need_shipping_address: SentinelOrValue[bool] = MISSING,
        is_flexible: SentinelOrValue[bool] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.send_invoice(
                    "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                    payload = "unique invoice payload", ...
                )
        """
        return await self.get_bot().send_invoice(
            self.id,
            title,
            description,
            provider_token,
            prices,
            invoice_payload=invoice_payload,
            photo_url=photo_url,
            need_name=need_name,
            need_email=need_email,
            need_phone_number=need_phone_number,
            need_shipping_address=need_shipping_address,
            is_flexible=is_flexible,
            **kwargs,
        )

    def send_chat_action(self, action: str) -> ChatActionContextManager:
        """
        Arguments:
            action (:obj:`str`):
                Type of action to broadcast. Choose one, depending on what the user is about to
                receive.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.constants import ChatAction

                await chat.send_chat_action(ChatAction.TYPING)

            .. code-block:: python

                from bale.constants import ChatAction

                async with chat.send_chat_action(ChatAction.TYPING):
                    # do something
        """
        return ChatActionContextManager(self.id, action, self.get_bot())

    async def copy_message(
        self,
        chat_id: int | str,
        message_id: int | str,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.copy_message(
                    6429983203, 6429983203
                )
        """
        return await self.get_bot().copy_message(
            chat_id,
            self.id,
            message_id,
            reply_to_message_id=reply_to_message_id,
            **kwargs,
        )

    async def send_sticker(self, sticker: "Sticker | FileInput", **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.send_sticker("FILE_ID", ...)
        """
        return await self.get_bot().send_sticker(self.id, sticker, **kwargs)

    async def send_media_group(
        self,
        media: "list[MediaInput]",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        **kwargs,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.send_media_group([
                    InputMediaPhoto("File ID", caption="example caption"),
                    InputMediaPhoto("File ID"),
                    InputMediaPhoto("File ID")
                ], ...)
        """
        return await self.get_bot().send_media_group(
            self.id, media, reply_markup=reply_markup, **kwargs
        )

    async def leave(self, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                chat = await bot.get_chat(6429983203)
                await chat.leave()
        """
        await self.get_bot().leave_chat(self.id, **kwargs)

    async def invite(self, user: "User | str | int", **kwargs):
        """|shortcut|

        Arguments:
            user:
                User object or Unique identifier for the target user.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                user = await bot.get_user(6429983203)
                await chat.add_user(user)
        """
        if isinstance(user, User):
            user = user.user_id

        await self.get_bot().invite_user(self.id, user, **kwargs)

    async def get_member(self, user: "User | str | int", **kwargs):
        """|shortcut|

        Arguments:
            user:
                User object or Unique identifier of the target user.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                user = await bot.get_user(6429983203)
                await chat.get_member(user)
                ...
                await chat.get_member(6429983203)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().get_chat_member(self.id, user, **kwargs)

    async def get_members(self, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                chat = await bot.get_user(6429983203)
                await chat.get_members(user)
        """
        return await self.get_bot().get_chat_members(self.id, **kwargs)

    async def set_title(self, title: str, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                chat = await bot.get_chat(6429983203)
                await chat.set_title('new title')
        """
        return await self.get_bot().set_chat_title(self.id, title, **kwargs)

    async def set_description(self, description: str, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                chat = await bot.get_chat(6429983203)
                await chat.set_description('new description')
        """
        return await self.get_bot().set_chat_description(self.id, description, **kwargs)

    async def ban_member(self, user: "User | str | int", **kwargs):
        """|shortcut|

        Arguments:
            user:
                User object or Unique identifier of the target user.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                user = await bot.get_user(6429983203)
                await chat.ban_member(user)
                ...
                await chat.ban_member(6429983203)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().ban_chat_member(self.id, user, **kwargs)

    async def unban_member(self, user: "User | str | int", **kwargs):
        """|shortcut|
        Arguments:
            user:
                User object or Unique identifier of the target user.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                user = await bot.get_user(6429983203)
                await chat.unban_member(user)
                ...
                await chat.unban_member(6429983203)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().unban_chat_member(self.id, user, **kwargs)

    async def set_photo(self, photo: PhotoSize | FileInput, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.set_photo("FILE_ID")
        """
        return await self.get_bot().set_chat_photo(self.id, photo, **kwargs)

    async def delete_photo(self, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.delete_photo()
        """
        return await self.get_bot().delete_chat_photo(self.id, **kwargs)

    async def get_members_count(self, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.get_members_count()
        """
        return await self.get_bot().get_chat_members_count(self.id, **kwargs)

    async def get_administrators(self, **kwargs):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await chat.get_administrators()
        """
        return await self.get_bot().get_chat_administrators(self.id, **kwargs)

    def __str__(self) -> str:
        return self.mention or self.full_name or str(self.id)
