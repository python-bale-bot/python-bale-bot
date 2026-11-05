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

from typing import TYPE_CHECKING, TypeAlias

from ._baleobject import BaleObject
from ._utils.context_manager import ChatActionContextManager
from ._utils.typehint import MISSING, SentinelOrValue

if TYPE_CHECKING:
    from pathlib import Path

    from bale import (Animation, Audio, Contact, Document,
                      InlineKeyboardMarkup, InputFile, InputMediaAnimation,
                      InputMediaAudio, InputMediaDocument, InputMediaPhoto,
                      InputMediaVideo, LabeledPrice, Location, Message,
                      PhotoSize, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Video, Voice)

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


class User(BaleObject):
    """This object represents a user account in the `Bale <https://ble.ir>`_ messenger.
    Instances of this class are typically received through API responses and other objects (such as messages and callback queries).

    Equality Conditions:
        1. The second object must be an instance of the :class:`User` class.
        2. The unique identifiers of the user accounts (:attr:`id`) must be equal.

    Attributes:
        id (:obj:`int`):
            Unique identifier for this user or bot.
        is_bot (:obj:`bool`):
            :obj:`True`, if this user is a bot.

            Note:
                In messages sent in discussion groups or channels, :attr:`Message.from_user`
                belongs to a channel, yet its :attr:`is_bot` attribute is set to :obj:`True`.
        first_name (:obj:`str`):
            User’s or bot’s first name.
        last_name (:obj:`str`, optional):
            User’s or bot’s last name.
        username (:obj:`str`, optional):
            User's or bot's username (without the '@' symbol).

            Note:
                For most existing bots, the username is required to end with ``bot``.
                However, some organizational or service bots are exempt from this rule,
                so the :attr:`is_bot` attribute should be relied upon as the definitive check.
                Additionally, there is no technical restriction preventing group, user,
                or channel names from ending with ``bot``.
    """

    __slots__ = ("id", "is_bot", "first_name", "last_name", "username")

    def __init__(
        self,
        id: int,
        is_bot: bool,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
    ) -> None:
        super().__init__()
        self._id = id
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

        self._lock()

    @property
    def chat_id(self) -> int:
        """Aliases for :attr:`id`"""
        return self.id

    @property
    def user_id(self) -> int:
        """Aliases for :attr:`id`"""
        return self.id

    @property
    def full_name(self) -> str:
        """Full name of the user, formed by concatenating :attr:`first_name` and :attr:`last_name`."""
        full = self.first_name
        if last_name := self.last_name:
            full += f" {last_name}"

        return full

    @property
    def mention(self) -> str | None:
        """Formatted mention of the user as ``@username`` if the :attr:`username` exists; otherwise, :obj:`None` is returned."""
        if u := self.username:
            return "@" + u

        return None

    async def send(
        self,
        text: str,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send("Hi, python-bale-bot!")
        """
        return await self.get_bot().send_message(
            self.chat_id, text, reply_markup=reply_markup
        )

    async def send_document(
        self,
        document: "Document | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_document("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_document(
            self.chat_id,
            document,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
        )

    async def send_photo(
        self,
        photo: "PhotoSize | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_photo("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_photo(
            self.chat_id,
            photo,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
        )

    async def send_video(
        self,
        video: "Video | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_video("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_video(
            self.chat_id,
            video,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
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
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_animation("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_animation(
            self.chat_id,
            animation,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
        )

    async def send_audio(
        self,
        audio: "Audio | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_audio("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_audio(
            self.chat_id,
            audio,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
        )

    async def send_voice(
        self,
        voice: "Voice | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        file_name: str | None = None,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_voice("FILE_ID", caption = "this is a caption", ...)
        """
        return await self.get_bot().send_voice(
            self.chat_id,
            voice,
            caption=caption,
            reply_markup=reply_markup,
            file_name=file_name,
        )

    async def send_location(
        self,
        location: "Location",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(
            self.chat_id, location, reply_markup=reply_markup
        )

    async def send_contact(
        self,
        contact: "Contact",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_contact(bale.Contact('09****', 'first name', 'last name))
        """
        return await self.get_bot().send_contact(
            self.chat_id, contact, reply_markup=reply_markup
        )

    async def send_invoice(
        self,
        title: str,
        description: str,
        provider_token: str,
        prices: list["LabeledPrice"],
        *,
        invoice_payload: SentinelOrValue[str] = MISSING,
        photo_url: SentinelOrValue[str] = MISSING,
        need_name: SentinelOrValue[bool] = False,
        need_phone_number: SentinelOrValue[bool] = False,
        need_email: SentinelOrValue[bool] = False,
        need_shipping_address: SentinelOrValue[bool] = False,
        is_flexible: SentinelOrValue[bool] = True,
    ):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_invoice(
                    "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                    payload = "unique invoice payload", ...
                )
        """
        return await self.get_bot().send_invoice(
            self.chat_id,
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
        )

    async def send_media_group(
        self,
        media: list["MediaInput"],
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
    ) -> tuple["Message"]:
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await user.send_media_group([
                    InputMediaPhoto("File ID", caption="example caption"),
                    InputMediaPhoto("File ID"),
                    InputMediaPhoto("File ID")
                ], ...)
        """
        return await self.get_bot().send_media_group(
            self.id, media, reply_markup=reply_markup, reply_to_message_id=self.id
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

                await user.send_chat_action(ChatAction.TYPING)

            .. code-block:: python

                from bale.constants import ChatAction

                async with user.send_chat_action(ChatAction.TYPING):
                    # do something
        """
        return ChatActionContextManager(self.id, action, self.get_bot())

    def __str__(self) -> str:
        return self.mention or self.full_name or str(self.id)
