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

from datetime import datetime
from typing import List, Dict, Optional, Union
from bale import (
    BaleObject,
    Chat, User, Document, Contact, Location, PhotoSize, Invoice, InlineKeyboardMarkup,
    MenuKeyboardMarkup, Video, Audio, BaseFile, Sticker, SuccessfulPayment, Animation, InputFile
)
from .helpers import parse_time

class Message(BaleObject):
    """This object shows a message.

    Attributes
    ----------
        message_id: str
            Unique message identifier inside this chat.
        from_user: Optional[:class:`bale.User`]
            Sender of the message; empty for messages sent to channels. For backward compatibility, this will contain a
            fake sender user in non-channel chats, if the message was sent on behalf of a chat.
        chat: :class:`bale.Chat`
            Conversation the message belongs to.
        date: :class:`datetime.datetime`
            Date the message was sent in Unix time.
        text: Optional[:class:`str`]
            Message Content
        caption: Optional[:class:`str`]
            Caption for the animation, audio, document, photo, video or voice.
        forward_from: Optional[:class:`bale.User`]
            For forwarded messages, sender of the original message.
        forward_from_chat: Optional[:class:`bale.Chat`]
            For messages forwarded from channels or from anonymous administrators, information about the original sender chat.
        reply_to_message: Optional[:class:`bale.Message`]
            For replies, the original message. Note that the Message object in this field will not contain further
            reply_to_message fields even if it itself is a reply.
        edit_date: Optional[:class:`datetime.datetime`]
            Date the message was last edited.
        contact: Optional[:class:`bale.Contact`]
            Message is a shared contact, information about the contact.
        location: Optional[:class:`bale.Location`]
            Message is a shared location, information about the location.
        document: Optional[:class:`bale.Document`]
            Message is a general file, information about the file.
        video: Optional[:class:`bale.Video`]
            Message is a video, information about the video.
        animation: Optional[:class:`bale.Animation`]
            Message is an animation, information about the animation.
        audio: Optional[:class:`bale.Audio`]
            Message is an audio, information about the Audio.
        sticker: Optional[:class:`bale.Sticker`]
            Message is a sticker, information about the sticker.
        new_chat_members: Optional[List[:class:`bale.User`]]
            New members that were added to the group or supergroup and information about them (the bot itself may be
            one of these members). This list is empty if the message does not contain new chat members.
        left_chat_member: Optional[:class:`bale.User`]
            A member was removed from the group, information about them (this member may be the bot itself).
        invoice: Optional[:class:`bale.Invoice`]
            Message is an invoice for a payment, information about the invoice.
        successful_payment: Optional[:class:`bale.SuccessfulPayment`]
            Message is a service message about a successful payment, information about the payment.
    """
    __slots__ = (
        "text", "caption", "from_user", "contact", "location", "chat", "message_id", "forward_from",
        "forward_from_chat", "forward_from_message_id", "date",
        "edit_date", "audio", "document", "video", "animation", "photos", "location", "sticker","invoice",
        "new_chat_members", "left_chat_member", "reply_to_message", "successful_payment"
    )

    def __init__(self, message_id: str, date: datetime, text: Optional[str], caption: Optional[str],
                 forward_from: Optional["User"], forward_from_chat: Optional["Chat"],
                 forward_from_message_id: Optional[str], from_user: Optional["User"],
                 document: Optional["Document"], contact: Optional["Contact"], edit_date: Optional[datetime],
                 location: Optional["Location"], chat: Optional["Chat"], video: Optional["Video"],
                 photos: Optional[List["PhotoSize"]], sticker: Optional["Sticker"],
                 reply_to_message: Optional["Message"], invoice: Optional["Invoice"],
                 audio: Optional["Audio"], successful_payment: Optional["SuccessfulPayment"],
                 animation: Optional["Animation"], new_chat_members: Optional[List["User"]], left_chat_member: Optional["User"]):
        super().__init__()
        self._id = message_id
        self.message_id = message_id
        self.date = date

        self.text = text
        self.chat = chat
        self.reply_to_message = reply_to_message
        self.from_user = from_user
        self.forward_from = forward_from
        self.forward_from_message_id = forward_from_message_id
        self.forward_from_chat = forward_from_chat
        self.edit_date = edit_date
        self.caption = caption
        self.document = document
        self.video= video
        self.animation = animation
        self.audio = audio
        self.photos = photos
        self.contact = contact
        self.location = location
        self.sticker = sticker
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member
        self.invoice = invoice
        self.successful_payment = successful_payment

        self._lock()

    @property
    def author(self):
        """An alias for :attr:`from_user`"""
        return self.from_user

    @property
    def attachment(self) -> Optional["BaseFile"]:
        """Optional[:class:`bale.BaseFile`]: Represents the message attachment. ``None`` if the message don't have any attachments"""
        attachment = self.video or self.photos or self.audio or self.document or self.animation
        if not attachment:
            return

        if isinstance(attachment, list):
            attachment = attachment[0]

        return attachment.base_file

    @property
    def content(self) -> Optional[str]:
        """Optional[:class:`str`]: Represents the message content. ``None`` if the message don't have text or caption"""
        return self.caption or self.text

    @property
    def chat_id(self) -> Optional[Union[str, int]]:
        """:class:`str` | :class:`int`: Represents the Unique identifier of Conversation the message belongs to."""
        return self.chat.id

    @property
    def reply_to_message_id(self) -> Optional[str]:
        """Optional[:class:`str`]: Represents the Unique identifier of Original message, if the message has been replied. ``None`` If the message is not replied"""
        if not self.reply_to_message:
            return

        return self.reply_to_message.message_id

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot) -> Optional["Message"]:
        data = BaleObject.parse_data(data)
        if not data:
            return None
        
        data["date"] = parse_time(data.get('date'))
        data["from_user"] = User.from_dict(data.pop('from', None), bot)
        data["chat"] = Chat.from_dict(data.get('chat'), bot)
        data["forward_from"] = User.from_dict(data.get('forward_from'), bot)
        data["forward_from_chat"] = Chat.from_dict(data.get('forward_from_chat'), bot)
        data["reply_to_message"] = Message.from_dict(data.get('reply_to_message'), bot)
        data["edit_date"] = parse_time(data.pop('edit_date', None))
        data["photos"] = [PhotoSize.from_dict(photo_payload, bot) for photo_payload in data.pop("photo", [])]
        data["document"] = Document.from_dict(data.get('document'), bot)
        data["audio"] = Audio.from_dict(data.get('audio'), bot)
        data["location"] = Location.from_dict(data.get('location'), bot)
        data["contact"] = Contact.from_dict(data.get('contact'), bot)
        data["animation"] = Animation.from_dict(data.get('animation'), bot)
        data["successful_payment"] = SuccessfulPayment.from_dict(data.get('successful_payment'), bot)
        data["sticker"] = Sticker.from_dict(data.get('sticker'), bot)
        data["invoice"] = Invoice.from_dict(data.get('invoice'), bot)
        data["new_chat_members"] = [User.from_dict(new_chat_member_payload, bot) for new_chat_member_payload in data.get('new_chat_members', [])] or None
        data["left_chat_member"] = User.from_dict(data.get('left_chat_member'), bot)

        return super().from_dict(data, bot)

    async def reply(self, text: str, *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        .. code:: python

            await message.reply("Hi, python-bale-bot!", components = None)
        """
        return await self.get_bot().send_message(self.chat_id, text, components=components,
                                           reply_to_message_id=self.message_id, delete_after=delete_after)

    async def forward(self, chat_id: Union[str, int]):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.forward_message`.

        .. code:: python

            await message.forward(1234)
        """
        return await self.get_bot().forward_message(chat_id, self.chat_id, self.message_id)

    async def reply_document(self, document: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        .. code:: python

            await message.reply_document(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_document(self.chat_id, document, caption=caption,
                                            components=components,
                                            reply_to_message_id=self.message_id,
                                            delete_after=delete_after)

    async def reply_photo(self, photo: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        .. code:: python

            await message.reply_photo(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_photo(self.chat_id, photo, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id,
                                         delete_after=delete_after)

    async def reply_video(self, video: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.

        .. code:: python

            await message.reply_video(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_video(self.chat_id, video, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id,
                                         delete_after=delete_after)

    async def reply_animation(self, animation: "InputFile", *, duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_animation`.

        .. code:: python

            await message.reply_animation(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_animation(self.chat_id, animation, duration=duration,
                                         width=width,
                                         height=height,
                                         caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id,
                                         delete_after=delete_after)

    async def reply_audio(self, audio: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await message.reply_audio(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.get_bot().send_video(self.chat_id, audio, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id,
                                         delete_after=delete_after)

    async def reply_location(self, location: "Location", *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await message.reply_location(bale.Location(35.71470468031143, 51.8568519168293))
        """
        return await self.get_bot().send_location(self.chat_id, location,
                                               components=components,
                                               reply_to_message_id=self.message_id,
                                               delete_after=delete_after)

    async def reply_contact(self, contact: "Contact", *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None, delete_after: Optional[Union[float, int]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_contact`.

        .. code:: python

            await message.reply_contact(bale.Contact('09****', 'first name', 'last name'))
        """
        return await self.get_bot().send_contact(self.chat_id, contact,
                                               components=components,
                                               reply_to_message_id=self.message_id,
                                               delete_after=delete_after)

    async def edit(self, text: str, *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None) -> Message:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.edit_message`.

        .. code:: python

            await message.edit("Bye!", components = None)
        """
        return await self.get_bot().edit_message(self.chat_id, self.message_id, text, components=components)

    async def delete(self, *, delay: Optional[Union[int, float]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.delete_message`.

        .. code:: python

            await message.delete(delay=5)
        """
        return await self.get_bot().delete_message(self.chat_id, self.message_id, delay=delay)
