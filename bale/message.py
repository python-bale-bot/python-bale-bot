from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from bale import Bot

from bale import (Chat, User, Document, ContactMessage)


class Message:
    """This object shows a message

    Args:
        message_id (str): Message ID.
        date (datetime.datetime): When the message has been sent.
        text (str): Message Text. Defaults to None.
        caption (str, optional): Message caption. Defaults to None.
        from_user (:class:`bale.User`): The user who has sent the message. Defaults to None.
        forward_from (:class:`bale.User`) no description. Defaults to None.
        contact (:class:`bale.ContactMessage`): Defaults to None.
        chat (:class:`bale.Chat`): The chat where the message is sent. Defaults to None.
        reply_to_message (:class:`bale.Message`)
        new_chat_members (:class:`bale.User`): User (An) who entered the chat. Defaults to None.
        left_chat_member (:class:`bale.User`): A user out of chat. Defaults to None.
        bot (:class:`bale.Bot`): Bot object. Defaults to None.
    """
    __slots__ = (
        "text", "caption", "from_user", "_author", "contact", "chat", "message_id", "forward_from", "date_code", "date", "edit_date",
        "audio", "document", "photo", "voice", "location", "invoice", "new_chat_members", "left_chat_member",
        "reply_to_message", "bot"
    )

    def __init__(self, message_id: int, date: datetime.datetime, text: str = None, caption: str = None,
                 forward_from: "User" = None, from_user: "User" = None, document: "Document" = None, contact: "ContactMessage" = None, chat: "Chat" = None,
                 reply_to_message: "Message" = None, bot: 'Bot' = None, **options):
        self.message_id: int = message_id if message_id is not None else None
        self.date = date if date is not None else None

        self.text: str | None = text if text is not None else None
        self.chat: Chat | None = chat if chat is not None else None
        self.reply_to_message: Message | None = reply_to_message if reply_to_message is not None else reply_to_message
        self.from_user: User | None = from_user if from_user is not None else None
        self.forward_from: User | None = forward_from if forward_from is not None else None
        self.caption: str | None = caption if caption is not None else None
        self.document = document if document is not None else None
        self.contact: ContactMessage | None = contact if contact is not None else None
        self.new_chat_members: List[User] | None = options.get("new_chat_members")
        self.left_chat_member: User | None = options.get("left_chat_member")
        self.bot: Bot = bot if bot is not None else None

    @property
    def author(self):
        if self.chat is not None:
            if self.chat.type == Chat.PRIVATE:
                return User(user_id=int(self.chat.chat_id), first_name=self.chat.first_name, last_name=self.chat.last_name,
                            username=self.chat.username, bot=self.bot)
            elif self.chat.type == Chat.GROUP:
                return User(bot=self.bot, user_id=self.from_user.user_id, first_name=self.from_user.first_name,
                            last_name=self.from_user.last_name, username=self.from_user.username)
        return None

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
            new_chat_members = []
            for i in data.get("new_chat_members"):
                new_chat_members.append(User.from_dict(bot=bot, data=i))
            options.__setattr__("new_chat_members", new_chat_members)
        if data.get("left_chat_member"):
            options.__setattr__("new_chat_members", User.from_dict(bot=bot, data=data.get("left_chat_member")))

        return cls(bot=bot, message_id=data.get("message_id"),
                   chat=Chat.from_dict(bot=bot, data=data.get("chat")) if data.get("chat") else None,
                   reply_to_message=Message.from_dict(bot=bot, data=data.get("reply_to_message")) if data.get(
                       "reply_to_message") else None, date=data.get("date"), text=data.get("text"),
                   from_user=User.from_dict(bot=bot, data=data.get("from")) if data.get("from") else None,
                   forward_from=User.from_dict(bot=bot, data=data.get("forward_from")) if data.get("forward_from") else None,
                   document=Document.from_dict(data=data.get("document")) if data.get("document") else None, **options)

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
            text (str)
            components (Components, dict): Defaults to None.

        Returns:
            :class:`bale.Message`
        """
        result = self.bot.send_message(chat_id=str(self.chat.chat_id), text=text, components=components,
                                       reply_to_message_id=str(self.message_id) if not self.chat.type == Chat.GROUP else None)
        return result

    def reply_invoice(self, title: str, description: str, provider_token: str, prices, photo_url=None, need_name=False,
                      need_phone_number=False, need_email=False, need_shipping_address=False, is_flexible=True):
        """:meth:`bale.Bot.send_invoice`

        Args:
            title (str): Invoice Title
            description (str): Invoice Description
            provider_token (str): You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
            prices (Price, dict)
            photo_url (str, optional): Photo URL of Invoice. Defaults to None.
            need_name (bool, optional): Get a name from "User"?. Defaults to False.
            need_phone_number (bool, optional): Get a Phone number from "User"?. Defaults to False.
            need_email (bool, optional): Get a Email from "User"?. Defaults to False.
            need_shipping_address (bool, optional): Get a Shipping Address from "User"?. Defaults to False.
            is_flexible (bool, optional): Is the Invoice Photo Flexible to the Payment button?. Defaults to True.

        Returns:
            :class:`Bale.Message`
        """
        message = self.bot.send_invoice(chat_id=self.chat.chat_id, title=title, description=description,
                                        provider_token=provider_token, prices=prices, photo_url=photo_url,
                                        need_name=need_name, need_email=need_email, need_phone_number=need_phone_number,
                                        need_shipping_address=need_shipping_address, is_flexible=is_flexible)
        return message

    async def edit(self, newtext: str, components=None):
        """:meth:`bale.Bot.edit_message`

        Args:
            newtext (str): New Content For Message.
            components (:class:`bale.Components`, optional): Components. Defaults to None.
        Raises:
            :class:`bale.Error`
        Return:
            :class:`requests.Response`
        """
        await self.bot.http.edit_message(self.chat.chat_id, self.message_id, newtext, components)
        self.text = newtext

    def delete(self):
        """:meth:`bale.Bot.delete_message`

        Return:
            bool: if done "True" if not "False"
        """
        message = self.bot.delete_message(chat_id=self.chat.chat_id, message_id=str(self.message_id))
        return message

    def __str__(self):
        return str(self.message_id)
