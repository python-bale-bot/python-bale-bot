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

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from bale import Bot

from bale import (Chat, User, Document, ContactMessage, Location, Photo, Invoice, InlineKeyboardMarkup,
                  MenuKeyboardMarkup, Video, Audio, File, SuccessfulPayment, Animation, InputFile)
from .helpers import parse_time

class Message:
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
        contact: Optional[:class:`bale.ContactMessage`]
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
        "forward_from_chat", "forward_from_message_id", "date_code", "date",
        "edit_date", "audio", "document", "video", "animation", "photos", "location", "invoice", "new_chat_members",
        "left_chat_member", "reply_to_message", "successful_payment", "bot"
    )

    def __init__(self, message_id: str, date: datetime, text: Optional[str] = None, caption: Optional[str] = None,
                 forward_from: Optional["User"] = None, forward_from_chat: Optional["Chat"] = None,
                 forward_from_message_id: Optional[str] = None, from_user: Optional["User"] = None,
                 document: Optional["Document"] = None,
                 contact: Optional["ContactMessage"] = None, location: Optional["Location"] = None,
                 chat: Optional["Chat"] = None, video: Optional["Video"] = None,
                 photos: Optional[List["Photo"]] = None, reply_to_message: Optional["Message"] = None,
                 invoice: Optional["Invoice"] = None, audio: Optional["Audio"] = None,
                 successful_payment: Optional["SuccessfulPayment"] = None, animation: Optional["Animation"] = None,
                 bot: 'Bot' = None, **options):
        self.message_id: str = message_id
        self.date = date

        self.text: Optional[str] = text
        self.chat: Optional["Chat"] = chat
        self.reply_to_message: Optional["Message"] = reply_to_message
        self.from_user: Optional["User"] = from_user
        self.forward_from: Optional["User"] = forward_from
        self.forward_from_message_id: Optional[str] = forward_from_message_id
        self.forward_from_chat: Optional["Chat"] = forward_from_chat
        self.caption: Optional[str] = caption
        self.document: Optional["Document"] = document
        self.video: Optional["Video"] = video
        self.animation: Optional["Animation"] = animation
        self.audio: Optional["Audio"] = audio
        self.photos: Optional[List["Photo"]] = photos
        self.contact: Optional["ContactMessage"] = contact
        self.location: Optional["Location"] = location
        self.new_chat_members: Optional[List["User"]] = options.get("new_chat_members")
        self.left_chat_member: Optional["User"] = options.get("left_chat_member")
        self.invoice: Optional["Invoice"] = invoice
        self.successful_payment = successful_payment
        self.bot: Optional[Bot] = bot

    @property
    def author(self):
        """An alias for :attr:`from_user`"""
        return self.from_user

    @property
    def attachment(self) -> Optional["File"]:
        """Optional[:class:`bale.File`]: Represents the message attachment. ``None`` if the message don't have any attachments"""
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
    def chat_id(self) -> Optional[str | int]:
        """:class:`str` | :class:`int`: Represents the Unique identifier of Conversation the message belongs to."""
        return self.chat.chat_id

    @property
    def reply_to_message_id(self) -> Optional[str]:
        """Optional[:class:`str`]: Represents the Unique identifier of Original message, if the message has been replied. ``None`` If the message is not replied"""
        if not self.reply_to_message:
            return

        return self.reply_to_message.message_id


    @classmethod
    def from_dict(cls, data: dict, bot):
        options = {}
        if data.get("new_chat_members"):
            options["new_chat_members"] = [User.from_dict(bot=bot, data=i) for i in data.get("new_chat_members")]
        if data.get("left_chat_member"):
            options["left_chat_member"] = User.from_dict(bot=bot, data=data.get("left_chat_member"))

        return cls(bot=bot, message_id=str(data.get("message_id")),
                   chat=Chat.from_dict(bot=bot, data=data.get("chat")) if data.get("chat") else None,
                   reply_to_message=Message.from_dict(bot=bot, data=data.get("reply_to_message")) if data.get(
                       "reply_to_message") else None, date=parse_time(int(data.get("date"))),
                   text=data.get("text"),
                   caption=data.get("caption"),
                   from_user=User.from_dict(bot=bot, data=data.get("from")) if data.get("from") else None,
                   forward_from=User.from_dict(bot=bot, data=data.get("forward_from")) if data.get(
                       "forward_from") else None,
                   forward_from_chat=Chat.from_dict(bot=bot, data=data.get("forward_from_chat")) if data.get(
                       "forward_from_chat") else None,
                   forward_from_message_id=str(data.get("forward_from_message_id")) if data.get(
                       "forward_from_message_id") else None,
                   document=Document.from_dict(bot=bot, data=data.get("document")) if data.get("document") else None,
                   contact=ContactMessage.from_dict(data=data.get("contact")) if data.get("contact") else None,
                   location=Location.from_dict(data=data.get("location")) if data.get("location") else None,
                   audio=Audio.from_dict(data=data.get("audio"), bot=bot) if data.get("audio") else None,
                   animation=Animation.from_dict(data=data.get("animation"), bot=bot) if data.get("animation") else None,
                   photos=[Photo.from_dict(data=photo_payload, bot=bot) for photo_payload in data.get("photo")] if data.get(
                       "photo") else None, video=Video.from_dict(data=data.get("video"), bot=bot) if data.get("video") else None,
                   successful_payment=SuccessfulPayment.from_dict(data.get("successful_payment")) if data.get("successful_payment") else None,
                   invoice=Invoice.from_dict(data=data.get("invoice")) if data.get("invoice") else None, **options)

    async def reply(self, text: str, *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_message`.

        .. code:: python

            await message.reply("Hi, python-bale-bot!", components = None)
        """
        return await self.bot.send_message(self.chat_id, text, components=components,
                                           reply_to_message_id=self.message_id)

    async def forward(self, chat_id: str | int):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.forward_message`.

        .. code:: python

            await message.forward(1234)
        """
        return await self.bot.forward_message(chat_id, self.chat_id, self.message_id)

    async def reply_document(self, document: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_document`.

        .. code:: python

            await message.reply_document(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_document(self.chat_id, document, caption=caption,
                                            components=components,
                                            reply_to_message_id=self.message_id)

    async def reply_photo(self, photo: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_photo`.

        .. code:: python

            await message.reply_photo(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_photo(self.chat_id, photo, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id)

    async def reply_video(self, video: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_video`.

        .. code:: python

            await message.reply_video(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_video(self.chat_id, video, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id)

    async def reply_animation(self, animation: "InputFile", *, duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_animation`.

        .. code:: python

            await message.reply_animation(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_animation(self.chat_id, animation, duration=duration,
                                         width=width,
                                         height=height,
                                         caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id)

    async def reply_audio(self, audio: "InputFile", *, caption: Optional[str] = None, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.send_audio`.

        .. code:: python

            await message.reply_audio(bale.InputFile("FILE_ID"), caption = "this is a caption", ...)
        """
        return await self.bot.send_video(self.chat_id, audio, caption=caption,
                                         components=components,
                                         reply_to_message_id=self.message_id)

    async def edit(self, text: str, *, components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None) -> Message:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.edit_message`.

        .. code:: python

            await message.edit("Bye!", components = None)
        """
        return await self.bot.edit_message(self.chat_id, self.message_id, text, components=components)

    async def delete(self, *, delay: Optional[Union[int, float]] = None):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.delete_message`.

        .. code:: python

            await message.delete(delay=5)
        """
        return await self.bot.delete_message(self.chat_id, self.message_id)

    def __str__(self):
        return str(self.message_id)

    def __eq__(self, other):
        return isinstance(other, Message) and self.message_id == other.message_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<Message message_id={self.message_id} from={self.from_user} chat={self.chat}>"
