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
from bale import BaleObject, User, ChatPhoto, Document, PhotoSize, Video, Animation, Audio
from bale.utils.types import FileInput, MediaInput
from typing import TYPE_CHECKING, Optional, List, Union, ClassVar, Dict

if TYPE_CHECKING:
    from bale import Message, User, InlineKeyboardMarkup, MenuKeyboardMarkup, LabeledPrice, Location, Contact, Sticker


__all__ = (
    "Chat",
)

class Chat(BaleObject):
    """This object indicates a chat.

    Attributes
    ----------
        id: :obj:`str`
            Unique identifier for this chat.
        type: :obj:`str`
            Type of chat.
        title: :obj:`str`, optional
            Title, for channels and group chats.
        username: :obj:`str`, optional
            Username, for private chats, supergroups and channels if available.
        first_name: :obj:`str`, optional
            First name of the other party in a private chat.
        last_name: :obj:`str`, optional
            Last name of the other party in a private chat.
        photo: :class:`bale.ChatPhoto`, optional
            Chat photo.
        invite_link: :obj:`str`, optional
            Primary invite link, for groups and channel. Returned only in :meth:`bale.Bot.get_chat()`.
    """
    PRIVATE: ClassVar[str] = "private"
    GROUP: ClassVar[str] = "group"
    CHANNEL: ClassVar[str] = "channel"
    __slots__ = (
        "__weakref__",
        "id",
        "type",
        "title",
        "username",
        "first_name",
        "last_name",
        "photo",
        "pinned_message",
        "all_members_are_administrators",
        "invite_link",
        "bot"
    )

    def __init__(self, chat_id: int, chat_type: str, title: Optional[str], username: Optional[str], first_name: Optional[str], last_name: Optional[str],
                 photo: Optional["ChatPhoto"], invite_link: Optional[str]):
        super().__init__()
        self._id = chat_id
        self.id = chat_id
        self.type = chat_type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo
        self.invite_link = invite_link

        self._lock()
        
    @property
    def is_private_chat(self) -> bool:
        return self.type == self.PRIVATE
    
    @property
    def is_group_chat(self) -> bool:
        return self.type == self.GROUP

    @property
    def is_channel_chat(self) -> bool:
        return self.type == self.CHANNEL

    async def send(self, text: str, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        .. code:: python

            await chat.send("hi, python-bale-bot!", components = None)
        """
        return await self.get_bot().send_message(self.id, text, components=components, delete_after=delete_after)

    async def send_document(self, document: Union["Document", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        .. code:: python

            await chat.send_document(bale.InputFile("FILE_ID"), caption = "this is caption", ...)
        """
        return await self.get_bot().send_document(self.id, document, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_photo(self, photo: Union["PhotoSize", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        .. code:: python

            await chat.send_photo(bale.InputFile("FILE_ID"), caption = "this is caption", ...)
        """
        return await self.get_bot().send_photo(self.id, photo, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_video(self, video: Union["Video", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.

        .. code:: python

            await chat.send_video(bale.InputFile("FILE_ID"), caption = "this is caption", ...)
        """
        return await self.get_bot().send_video(self.id, video, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_animation(self, animation: Union["Animation", FileInput], *, duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_animation`.

        .. code:: python

            await chat.send_animation(bale.InputFile("FILE_ID"), caption = "this is caption", ...)
        """
        return await self.get_bot().send_animation(self.id, animation, duration=duration, width=width, height=height, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_audio(self, audio: Union["Audio", FileInput], *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None, file_name: Optional[str] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await chat.send_audio(bale.InputFile("FILE_ID"), caption = "this is caption", ...)
        """
        return await self.get_bot().send_audio(self.id, audio, caption=caption, components=components, delete_after=delete_after, file_name=file_name)

    async def send_location(self, location: "Location", delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_location`.

        .. code:: python

            await chat.send_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(self.id, location, delete_after=delete_after)

    async def send_contact(self, contact: "Contact", delete_after: Optional[Union[float, int]] = None) -> "Message":
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.

        .. code:: python

            await chat.send_contact(Contact('09****', 'first name', 'last name))
        """
        return await self.get_bot().send_contact(self.id, contact, delete_after=delete_after)

    async def send_invoice(self, title: str, description: str, provider_token: str, prices: List["LabeledPrice"], *,
                   payload: Optional[str] = None, photo_url: Optional[str] = None, need_name: Optional[bool] = False,
                   need_phone_number: Optional[bool] = False, need_email: Optional[bool] = False,
                   need_shipping_address: Optional[bool] = False, is_flexible: Optional[bool] = True,
                   delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_invoice`.

        .. code:: python

            await chat.send_invoice(
                "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                payload = "unique invoice payload", ...
            )
        """
        return await self.get_bot().send_invoice(self.id, title, description, provider_token, prices,
                                        payload=payload, photo_url=photo_url, need_name=need_name, need_email=need_email,
                                        need_phone_number=need_phone_number, need_shipping_address=need_shipping_address, is_flexible=is_flexible,
                                        delete_after=delete_after)

    async def copy_message(self, chat_id: Union[int, str], message_id: Union[int, str], reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.copy_message`.

        .. code:: python

            await chat.copy_message(
                1234, 1234
            )
        """
        return await self.get_bot().copy_message(chat_id, self.id, message_id, reply_to_message_id=reply_to_message_id, delete_after=delete_after)

    async def send_sticker(self, sticker: Union["Sticker", FileInput], *, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_sticker`.

        .. code:: python

            await chat.send_sticker("FILE_ID", ...)
        """
        return await self.get_bot().send_sticker(self.id, sticker, delete_after=delete_after)

    async def send_media_group(self, media: List[MediaInput], *,
                    components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_media_group`.

        .. code:: python

            await chat.send_media_group([
                InputMediaPhoto("File ID", caption="example caption"),
                InputMediaPhoto("File ID"),
                InputMediaPhoto("File ID")
            ], ...)
        """
        return await self.get_bot().send_media_group(self.id, media, components=components)

    async def leave(self):
        """
        For the documentation of the method, please see :meth:`bale.Bot.leave_chat`.

        .. code:: python

            chat = await bot.get_chat(1234)
            await chat.leave()
        """
        await self.get_bot().leave_chat(self.id)

    async def add_user(self, user: Union["User", str, int]):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.invite_user`.

        .. code:: python

            user = await bot.get_user(1234)
            await chat.add_user(user)
        """
        if isinstance(user, User):
            user = user.user_id

        await self.get_bot().invite_user(self.id, user)

    async def get_chat_member(self, user: Union["User", str, int]):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_member`.

        .. code:: python

            user = await bot.get_user(1234)
            await chat.get_chat_member(user)
            ...
            await chat.get_chat_member(1234)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().get_chat_member(self.id, user_id=user)

    async def ban_chat_member(self, user: Union["User", str, int]):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.ban_chat_member`.

        .. code:: python

            user = await bot.get_user(1234)
            await chat.ban_chat_member(user)
            ...
            await chat.ban_chat_member(1234)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().ban_chat_member(self.id, user)

    async def unban_chat_member(self, user: Union["User", str, int], *, only_if_banned: Optional[bool] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.unban_chat_member`.

        .. code:: python

            user = await bot.get_user(1234)
            await chat.unban_chat_member(user)
            ...
            await chat.unban_chat_member(1234)
        """
        if isinstance(user, User):
            user = user.user_id

        return await self.get_bot().unban_chat_member(self.id, user, only_if_banned=only_if_banned)

    async def set_photo(self, photo: Union[PhotoSize, FileInput]):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.set_chat_photo`.

        .. code:: python

            await chat.set_photo(bale.InputFile("FILE_ID"))
        """
        return await self.get_bot().set_chat_photo(self.id, photo)

    async def get_chat_members_count(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_members_count`.

        .. code:: python

            await chat.get_chat_members_count()
        """
        return await self.get_bot().get_chat_members_count(self.id)

    async def get_chat_administrators(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_chat_administrators`.

        .. code:: python

            await chat.get_chat_administrators()
        """
        return await self.get_bot().get_chat_administrators(self.id)

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot):
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["chat_id"] = data.pop("id")
        data["chat_type"] = data.pop("type")
        data["photo"] = ChatPhoto.from_dict(data.get('photo'), bot)

        return super().from_dict(data, bot)
