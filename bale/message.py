"""
    MIT License

    Copyright (c) 2022 kian Ahmadian

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
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from bale import Bot

from bale import (Chat, ChatType, User, Document, ContactMessage, Photo, Invoice)


class Message:
    """This object shows a message

    Args:
        message_id (str): Message ID.
        date (datetime.datetime): When the message has been sent.
        text (str): Message Text. Defaults to None.
        caption (str): Message caption. Defaults to None.
        from_user (:class:`bale.User`): The user who has sent the message. Defaults to None.
        forward_from (:class:`bale.User`) no description. Defaults to None.
        contact (:class:`bale.ContactMessage`): Defaults to None.
        chat (:class:`bale.Chat`): The chat where the message is sent. Defaults to None.
        reply_to_message (:class:`bale.Message`)
        new_chat_members (:class:`bale.User`): User (An) who entered the chat. Defaults to None.
        left_chat_member (:class:`bale.User`): A user out of chat. Defaults to None.
        invoice (:class:`bale.Invoice`): Message invoice.
        bot (:class:`bale.Bot`): Bot object. Defaults to None.
    """
    __slots__ = (
        "text", "caption", "from_user", "_author", "contact", "chat", "message_id", "forward_from", "forward_from_message_id", "date_code", "date", "edit_date",
        "audio", "document", "photos", "voice", "location", "invoice", "new_chat_members", "left_chat_member",
        "reply_to_message", "invoice", "bot"
    )

    def __init__(self, message_id: str, date: datetime, text: str = None, caption: str = None,
                 forward_from: "User" = None, forward_from_message_id: str = None, from_user: "User" = None, document: "Document" = None, contact: "ContactMessage" = None, chat: "Chat" = None,
                 photos: List["Photo"] = None, reply_to_message: "Message" = None, invoice: "Invoice" = None, bot: 'Bot' = None, **options):
        self.message_id: str = message_id if message_id is not None else None
        self.date = date if date is not None else None

        self.text: str | None = text if text is not None else None
        self.chat: Chat | None = chat if chat is not None else None
        self.reply_to_message: Message | None = reply_to_message if reply_to_message is not None else reply_to_message
        self.from_user: User | None = from_user if from_user is not None else None
        self.forward_from: User | None = forward_from if forward_from is not None else None
        self.forward_from_message_id: str = forward_from_message_id if forward_from_message_id is not None else None
        self.caption: str | None = caption if caption is not None else None
        self.document = document if document is not None else None
        self.photos = photos if photos is not None else None
        self.contact: ContactMessage | None = contact if contact is not None else None
        self.new_chat_members: List[User] | None = options.get("new_chat_members")
        self.left_chat_member: User | None = options.get("left_chat_member")
        self.invoice = invoice
        self.bot: Bot = bot if bot is not None else None

    @property
    def author(self):
        return self.from_user

    @property
    def content(self):
        return self.caption or self.text

    @content.setter
    def content(self, _value):
        if not isinstance(_value, str):
            raise TypeError(f"{_value} is not str. this is a {_value.__class__ if _value else _value}")
        if self.caption:
            self.caption = _value
        elif self.text:
            self.text = _value

    @property
    def chat_id(self):
        if self.chat is not None:
            return self.chat.chat_id
        return None

    @property
    def reply_to_message_id(self):
        if self.reply_to_message:
            return self.reply_to_message.message_id
        return None

    @reply_to_message_id.setter
    def reply_to_message_id(self, _value):
        if not isinstance(_value, int):
            raise TypeError(f"{_value} is not str. this is a {_value.__class__ if _value else _value}")

        if self.reply_to_message:
            self.reply_to_message.message_id = _value

    @classmethod
    def from_dict(cls, data: dict, bot):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        options = {}
        if data.get("new_chat_members"):
            options["new_chat_members"] = [User.from_dict(bot=bot, data=i) for i in data.get("new_chat_members")]
        if data.get("left_chat_member"):
            options["left_chat_member"] = User.from_dict(bot=bot, data=data.get("left_chat_member"))

        return cls(bot=bot, message_id=str(data.get("message_id")),
                   chat=Chat.from_dict(bot=bot, data=data.get("chat")) if data.get("chat") else None,
                   reply_to_message=Message.from_dict(bot=bot, data=data.get("reply_to_message")) if data.get(
                       "reply_to_message") else None, date=datetime.fromtimestamp(int(data.get("date"))), text=data.get("text"),
                   from_user=User.from_dict(bot=bot, data=data.get("from")) if data.get("from") else None,
                   forward_from=User.from_dict(bot=bot, data=data.get("forward_from")) if data.get("forward_from") else None,
                   forward_from_message_id=str(data.get("forward_from_message_id")) if data.get("forward_from_message_id") else None,
                   document=Document.from_dict(data=data.get("document")) if data.get("document") else None,
                   photo=[Photo.from_dict(data=photo_payload) for photo_payload in data.get("photo")] if data.get("photo") else None,
                   invoice=Invoice.from_dict(data=data.get("invoice")) if data.get("invoice") else None, **options)

    def to_dict(self):
        data = {"message_id": self.message_id, "date": self.date, "text": self.text}

        if self.chat:
            data["chat"] = self.chat.to_dict()
        if self.from_user:
            data["from"] = self.from_user.to_dict()
        if self.caption:
            data["caption"] = self.caption
        if self.document:
            data["document"] = self.document.to_dict()
        if self.photos:
            data["photo"] = [photo.to_dict() for photo in self.photos]
        if self.contact:
            data["contact"] = self.contact.to_dict()
        if self.new_chat_members:
            data["new_chat_members"] = self.new_chat_members
        if self.forward_from:
            data["forward_from"] = self.forward_from.to_dict()
        if self.left_chat_member:
            data["left_chat_member"] = self.left_chat_member.to_dict()
        if self.reply_to_message_id:
            data["reply_to_message_id"] = self.reply_to_message_id

        return data

    def reply(self, text: str, components=None):
        """:meth:`bale.Bot.send_message`

        Args:
            text (str): Message Text.
            components (:class:`bot.Components`|:class:`bale.RemoveComponents`): Message Components.
        Raises:
            :class:`bale.Error`
        Returns:
            :class:`bale.Message`: On success, the sent Message is returned."""
        result = self.bot.send_message(chat_id=self.chat.chat_id, text=text, components=components,
                                       reply_to_message_id=str(self.message_id) if not self.chat.type.is_group_chat() else None)
        return result

    def reply_invoice(self, title: str, description: str, provider_token: str, prices, photo_url=None, need_name=False,
                      need_phone_number=False, need_email=False, need_shipping_address=False, is_flexible=True):
        """:meth:`bale.Bot.send_invoice`

        Args:
            title (str): Invoice Title
            description (str): Invoice Description
            provider_token (str): You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
            prices (List[:class:`bale.Price`]): A list of prices.
            photo_url (str): Photo URL of Invoice. Defaults to None.
            need_name (bool): Get a name from "User"?. Defaults to False.
            need_phone_number (bool): Get a Phone number from "User"?. Defaults to False.
            need_email (bool): Get a Email from "User"?. Defaults to False.
            need_shipping_address (bool): Get a Shipping Address from "User"?. Defaults to False.
            is_flexible (bool): Is the Invoice Photo Flexible to the Payment button?. Defaults to True.
        Returns:
            :class:`Bale.Message`
        """
        message = self.bot.send_invoice(chat_id=self.chat.chat_id, title=title, description=description,
                                        provider_token=provider_token, prices=prices, photo_url=photo_url,
                                        need_name=need_name, need_email=need_email, need_phone_number=need_phone_number,
                                        need_shipping_address=need_shipping_address, is_flexible=is_flexible)
        return message

    async def edit(self, text: str = None, components=None):
        """:meth:`bale.Bot.edit_message`

        Args:
            text (str): New Content For Message.
            components (:class:`bale.Components`|:class:`bale.RemoveComponents`): Components.
        Raises:
            :class:`bale.Error`
        Return:
            :class:`dict`
        """
        result = await self.bot.edit_message(self.chat.chat_id, self.message_id, text, components)
        self.text = text
        return result

    def delete(self):
        """:meth:`bale.Bot.delete_message`

        Return:
            bool: if done "True" if not "False"
        """
        message = self.bot.delete_message(chat_id=self.chat.chat_id, message_id=str(self.message_id))
        return message

    def __str__(self):
        return str(self.message_id)
