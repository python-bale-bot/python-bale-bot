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
from typing import TYPE_CHECKING, Optional, List, Union, Dict
from bale import BaleObject, Document, PhotoSize, Video, Audio, Animation
from bale.utils.types import FileInput, MediaInput
if TYPE_CHECKING:
    from bale import InlineKeyboardMarkup, MenuKeyboardMarkup, LabeledPrice, Location, Contact, InputFile, Message


class User(BaleObject):
    """This object represents a Bale user or bot.

    Attributes
    ----------
        id: :obj:`int`
            Unique identifier for this user or bot.
        is_bot: :obj:`bool`, optional
            ``True``, if this user is a bot.
        first_name: :obj:`str`
            User’s or bot’s first name.
        last_name: :obj:`str`, optional
            User’s or bot’s last name.
        username: :obj:`str`, optional
            User’s or bot’s username.
    """
    __slots__ = (
        "__weakref__",
        "is_bot",
        "first_name",
        "last_name",
        "username",
        "id"
    )

    def __init__(self, user_id: int, is_bot: bool, first_name: str, last_name: Optional[str] = None,
                 username: Optional[str] = None):
        super().__init__()
        self._id = user_id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.id = user_id

        self._lock()

    @property
    def mention(self) -> str | None:
        """:obj:`str`, optional: mention user with username."""
        if self.username:
            return "@" + self.username

        return None

    @property
    def chat_id(self) -> int:
        """Aliases for :attr:`id`"""
        return self.id

    @property
    def user_id(self) -> int:
        """Aliases for :attr:`id`"""
        return self.id

    async def send(self, text: str, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        .. code:: python

            await user.send("Hi, python-bale-bot!", components = None)
        """
        return await self.get_bot().send_message(self.chat_id, text, components=components, delete_after=delete_after)

    async def send_document(self, document: Union["Document", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        .. code:: python

            await user.send_document(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_document(self.chat_id, document, caption=caption, components=components, delete_after=delete_after, file_name = file_name)

    async def send_photo(self, photo: Union["PhotoSize", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        .. code:: python

            await user.send_photo(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_photo(self.chat_id, photo, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_video(self, video: Union["Video", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.

        .. code:: python

            await user.send_video(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_video(self.chat_id, video, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_animation(self, animation: Union["Animation", FileInput], *, duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_animation`.

        .. code:: python

            await user.send_animation(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_animation(self.chat_id, animation, duration=duration, width=width, height=height, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_audio(self, audio: Union["Audio", InputFile], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await user.send_audio(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_audio(self.chat_id, audio, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_location(self, location: "Location", *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_location`.

        .. code:: python

            await user.send_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(self.chat_id, location, components=components, delete_after=delete_after)

    async def send_contact(self, contact: "Contact", *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.

        .. code:: python

            await user.send_contact(bale.Contact('09****', 'first name', 'last name))
        """
        return await self.get_bot().send_contact(self.chat_id, contact, components=components, delete_after=delete_after)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["LabeledPrice"], *, payload: Optional[str] = None,
               photo_url: Optional[str] = None, need_name: Optional[bool] = False, need_phone_number: Optional[bool] = False,
               need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True,
               delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`.

        .. code:: python

            await user.send_invoice(
                "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                payload = "unique invoice payload", ...
            )
        """
        return await self.get_bot().send_invoice(self.chat_id, title, description, provider_token, prices,
                                           payload=payload, photo_url=photo_url, need_name=need_name, need_email=need_email,
                                           need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible,
                                           delete_after=delete_after)

    async def send_media_group(self, media: List[MediaInput], *,
                    components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None) -> List["Message"]:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_media_group`.

        .. code:: python

            await user.send_media_group([
                InputMediaPhoto("File ID", caption="example caption"),
                InputMediaPhoto("File ID"),
                InputMediaPhoto("File ID")
            ], ...)
        """
        return await self.get_bot().send_media_group(self.id, media, components=components, reply_to_message_id=self.id)

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot):
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["user_id"] = data.pop("id")

        return super().from_dict(data, bot)
