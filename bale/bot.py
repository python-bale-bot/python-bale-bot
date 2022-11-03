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
import asyncio
from typing import Callable, Dict, Tuple, List
from builtins import enumerate, reversed
from error import NotFound
from bale import (Message, Update, User, Components, RemoveComponents, Chat, Price, ChatMember, HTTPClient, Updater,
                  Photo, Document)


__all__ = (
    "Bot"
)


class _Loop:
    __slots__ = ()
    
    
_loop = _Loop()


class Bot:
    """This object represents a Bale Bot.

    Parameters
    ----------
        token: str 
            Bot Token
    """
    __slots__ = (
        "loop",
        "token",
        "loop",
        "events",
        "listeners",
        "updater",
        "_user",
        "http",
        "_closed"
    )

    def __init__(self, token: str):
        self.loop = _loop
        self.token = token
        self.http: HTTPClient = HTTPClient(loop=self.loop, token=token)
        self._user = None
        self.updater = Updater(self)
        self.events: Dict[str, List[Callable]] = {}
        self.listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self._closed = False

    def listen(self, event_name):
        """Register a Event"""
        def decorator(func):
            self.add_event(event_name, func)
        return decorator

    def add_event(self, event: str, function):
        """Register an Event with event name"""
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(f"{function.__name__} is not a Coroutine Function")

        if not self.events.get(event):
            self.events[event] = list()

        self.events[event].append(function)

    def remove_event(self, event: str, function = None):
        """Register an Event with event name"""
        result = self.events.get(event)
        if not result:
            raise TypeError(f"{event} not in Events")

        if not function:
            del self.events[event]
            return

        if not function in result:
            raise TypeError(f"{function.__name__} not in Event Functions")

        del self.events[event][function]

    def wait_for(self, event_name: str, check = None, timeout = None):
        """Wait for an event"""
        self.loop: asyncio.AbstractEventLoop
        future = self.loop.create_future()
        event_name = event_name.lower()
        if not check:
            check = lambda: True

        listeners = self.listeners.get(event_name)
        if not listeners:
            listeners = []
            self.listeners[event_name] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout = timeout)

    @property
    def user(self) -> "User" or None:
        """Represents the connected client. ``None`` if not logged in"""
        return self._user

    async def __aenter__(self):
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        await self.http.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def close(self):
        """Close http Events and bot"""
        await self.http.close()
        self._closed = True

    def is_closed(self):
        """:class:`bool`: Connection Status"""
        return self._closed

    async def run_event(self, core, event_name, *args, **kwargs):
        try:
            await core(*args, **kwargs)
        except Exception as ext:
            await self.on_error(event_name, ext)

    def call_to_run_event(self, core, event_name, *args, **kwargs):
        task = self.run_event(core, event_name, *args, **kwargs)
        self.loop: asyncio.AbstractEventLoop
        return self.loop.create_task(task, name = event_name)

    def dispatch(self, event_name, /, *args, **kwargs):
        method = "on_" + event_name
        listeners = self.listeners.get(event_name)
        if listeners:
            removed = []
            for index, (future, check) in enumerate(listeners):
                if future.cancelled():
                    removed.append(index)
                    continue
                try:
                    result = check(*args)
                except Exception as __exception:
                    future.set_exception(__exception)
                    removed.append(index)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(index)

            if len(listeners) == len(removed):
                self.listeners.pop(event_name)
            else:
                for index in reversed(removed):
                    del listeners[index]

        events_core = self.events.get(method)
        if events_core:
            for event_core in events_core:
                self.call_to_run_event(event_core, method, *args, **kwargs)

    async def on_error(self, event_name, error):
        """a Event for get errors when exceptions"""
        print("error", event_name, error)

    async def get_bot(self) -> User:
        """Get bot information

        Returns
        -------
            :class:`Bale.User` :
                Bot User information.
        Raises
        ------
            :class:`Bale.Error`
        """
        response = await self.http.get_bot()
        return User.from_dict(data=response.result, bot=self)

    async def delete_webhook(self) -> bool:
        """This service is used to remove the webhook set for the bot.

        Returns
        -------
            bool:
                ``True`` else ``False`` if not done
        """
        response = await self.http.delete_webhook()
        return response.result or False

    async def send_message(self, chat: "Chat" | "User", text: str = None, components: "Components" | "RemoveComponents" =None, reply_to_message_id: str = None) -> Message | None:
        """This service is used to send text messages.

        Parameters
        ----------
            chat: :class:`bale.Chat` | :class:`bale.User`
                Chat
            text: :class:`str`
                Message Text
            components: :class:`bale.Components` | :class:`bale.RemoveComponents`
                Message Components
            reply_to_message_id: :class:`str`
                Reply Message ID
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            Optional[:class:`bale.Message`]:
                The Message or ``None`` if message not sent
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        if not isinstance(components, (Components, RemoveComponents)):
            raise TypeError(
                "components param must be type of Components or RemoveComponents"
            )

        if not isinstance(reply_to_message_id, (int, str)):
            raise TypeError(
                "reply_to_message_id param must be type of int or str"
            )

        if components:
            components = components.to_dict()
        if reply_to_message_id:
            reply_to_message_id = reply_to_message_id

        response = await self.http.send_message(str(chat.chat_id), text, components=components, reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_document(self, chat: "Chat" | "User", document: bytes | str | "Document", caption: str = None, reply_to_message_id: str = None):
        """This service is used to send document.

        Parameters
        ----------
        chat: :class:`bale.Chat` | :class:`bale.User`
            Chat
        document: :class:`bytes` | :class:`str` | :class:`bale.Document`
            Photo
        caption: :class:`str`
            Message caption
        reply_to_message_id: :class:`str`
            Reply Message ID

        Raises
        ------
            :class:`bale.Error`

        Returns
        --------
            Optional[:class:`bale.Message`]:
                The Message or ``None`` if message not sent
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        if not isinstance(document, (bytes, str, Document)):
            raise TypeError(
                "document param must be type of bytes, str or Document"
            )

        if not isinstance(reply_to_message_id, (int, str)):
            raise TypeError(
                "reply_to_message_id param must be type of int or str"
            )

        if isinstance(document, Document):
            document = document.file_id

        response = await self.http.send_document(chat.chat_id, document, caption=caption)
        return Message.from_dict(data=response.result, bot=self)

    async def send_photo(self, chat: "Chat" | "User", photo: bytes | str | "Photo", caption: str = None, reply_to_message_id: str = None):
        """This service is used to send photo.

        Parameters
        ----------
        chat: :class:`bale.Chat` | :class:`bale.User`
            Chat
        photo: :class:`bytes` | :class:`str` | :class:`bale.Photo`
            Photo
        caption: :class:`str`
            Message caption
        reply_to_message_id: :class:`str`
            Reply Message ID

        Raises
        ------
            :class:`bale.Error`

        Returns
        --------
            Optional[:class:`bale.Message`]:
                The Message or ``None`` if message not sent
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        if not isinstance(photo, (bytes, str, Photo)):
            raise TypeError(
                "photo param must be type of bytes, str or Photo"
            )

        if isinstance(photo, Photo):
            photo = photo.file_id

        response = await self.http.send_photo(str(chat.chat_id), photo, caption=caption, reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_invoice(self, chat: "Chat" | "User", title: str, description: str, provider_token: str, prices: List[Price], photo_url: str = None, need_name: bool = False, need_phone_number: bool = False, need_email: bool = False, need_shipping_address: bool = False, is_flexible: bool = True) -> Message | None:
        """You can use this service to send money request messages.

        Parameters
        ----------
        chat: :class:`bale.Chat` | :class:`bale.User`
            Chat
        title: str
            Invoice Title
        description: str
            Invoice Description
        provider_token: str
            You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
        prices: List[:class:`bale.Price`]
            A list of prices.
        photo_url: str
            Photo URL of Invoice. Defaults to None.
        need_name: bool
            Get a name from "User"?. Defaults to False.
        need_phone_number: bool
            Get a Phone number from "User"?. Defaults to False.
        need_email: bool
            Get a Email from "User"?. Defaults to False.
        need_shipping_address: bool
            Get a Shipping Address from "User"?. Defaults to False.
        is_flexible: bool
            Is the Invoice Photo Flexible to the Payment button?. Defaults to True.

        Returns
        -------
            :class:`Bale.Message`
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        prices = [price.to_dict() for price in prices if isinstance(price, Price)]
        response = await self.http.send_invoice(str(chat.chat_id), title, description, provider_token, prices, photo_url, need_name, need_phone_number, need_email, need_shipping_address, is_flexible)
        return Message.from_dict(data=response.result, bot=self)

    async def edit_message(self, chat: "Chat" | "User", message_id: str, text: str, components: "Components" | "RemoveComponents"=None) -> Message:
        """You can use this service to edit text messages that you have already sent through the arm.

        Parameters
        ----------
            chat: :class:`bale.Chat`
                chat
            message_id: str
                message id
            text: str
                New Content For Message.
            components: Optional[:class:`bale.Components` | :class:`bale.RemoveComponents`]
                message components
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            :class:`dict`
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        if not isinstance(components, (Components, RemoveComponents)):
            raise TypeError(
                "components param must be type of Components or RemoveComponents"
            )

        if not isinstance(message_id, (int, str)):
            raise TypeError(
                "message_id param must be type of int or str"
            )

        if components:
            components = components.to_dict()

        response = await self.http.edit_message(str(chat.chat_id), message_id, text, components=components)
        return response.result

    async def delete_message(self, chat: "Chat" | "User", message_id: str | int) -> bool:
        """You can use this service to delete a message that you have already sent through the arm.

        In Channel or Group:
            If it is a group or channel Manager, it can delete a message from (group or channel).

        In private message (PV):
            If the message was sent by a bot, it can be deleted with this method

        Parameters
        ----------
            chat: :class:`bale.Chat`
                chat
            message_id: str | int
                message id
        Returns
        -------
            bool:
                ``True`` if done else ``False``
        """
        if not isinstance(chat, (Chat, User)):
            raise TypeError(
                "chat param must be type of Chat or User"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )

        response = await self.http.delete_message(str(chat.chat_id), message_id)
        return response.result or False

    async def get_chat(self, chat_id: int | str) -> Chat | None:
        """This service can be used to receive personal information that has previously interacted with the arm.

        Parameters
        ----------
            chat_id: int | str
                chat id
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            Optional[:class:`bale.Chat`]
                The chat or ``None`` if not found.
        """
        if not isinstance(chat_id, (int, str)):
            raise TypeError(
                "chat_id param must be type of int or str"
            )

        try:
            response = await self.http.get_chat(str(chat_id))
        except NotFound:
            return None
        else:
            return Chat.from_dict(response.result, bot=self)

    async def get_user(self, user_id: int | str) -> "User" | None:
        """This Method almost like :class:`bale.Bot.get_chat` , but this a filter that only get user.

        Parameters
        ----------
            user_id: int
                user id
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            Optional[:class:`bale.User`]
                The user or ``None`` if not found.
        """
        if not isinstance(user_id, (int, str)):
            raise TypeError(
                "user_id param must be type of int or str"
            )

        chat = await self.get_chat(user_id)
        if chat and chat.type.is_private_chat():
            return User.from_dict(chat.to_dict(), self)

        return None

    async def get_chat_member(self, chat: "Chat", user_id: int) -> "ChatMember" | None:
        """
        Parameters
        ----------
            chat: :class:`bale.Chat`
                chat
            user_id: int
                user

        Raises
        ------
            :class:`bale.Error`

        Returns
        -------
            Optional[:class:`bale.ChatMember`]:
                The chat member or ``None`` if not found.
        """
        if not isinstance(chat, Chat):
            raise TypeError(
                "chat param must be type of Chat"
            )

        if not isinstance(user_id, int):
            raise TypeError(
                "user_id param must be type of int"
            )

        try:
            response = await self.http.get_chat_member(chat_id=str(chat.chat_id), member_id=str(user_id))
        except NotFound:
            return None
        else:
            return ChatMember.from_dict(response.result)

    async def invite_to_chat(self, chat: "Chat", user: "User") -> bool:
        """Invite user to the chat

        Parameters
        ----------
            chat: :class:`bale.Chat`
                chat
            user: :class:`bale.User`
                user

        Raises
        ------
            :class:`bale.Error`
        
        Returns
        -------
            bool:
                ``True`` when user added to chat else ``False``
        """
        if not isinstance(chat, Chat):
            raise TypeError(
                f"chat is not a Chat object. this is a {chat.__class__} !"
            )

        if not isinstance(user, User):
            raise TypeError(
                "user param must be type of User"
            )
        response = await self.http.invite_to_chat(str(chat.chat_id), str(user.user_id))
        return response.result or False

    async def leave_chat(self, chat: "Chat"):
        """Leave bot from a Chat

        Parameters
        ----------
            chat: :class:`bale.Chat`
                chat
        
        Raises
        ------
            :class:`bale.Error`

        Returns
        -------
            bool:
                ``True`` when bot leaved from chat else ``False``
        """
        if not isinstance(chat, Chat):
            raise TypeError(
                "chat param must be type of Chat"
            )
        response = await self.http.leave_chat(str(chat.chat_id))
        return response.result or False

    async def get_chat_members_count(self, chat: "Chat") -> int | None:
        """
        Parameters
        ----------
            chat: :class:`bale.Chat` 

        Raises
        ------
            :class:`bale.Error`
                Group ID

        Returns
        --------
            Optional[int]:
                int or ``None`` if chat not found.
        """
        if not isinstance(chat, Chat):
            raise TypeError(
                "chat param must be type of Chat"
            )

        response = await self.http.get_chat_members_count(str(chat.chat_id))
        return response.result

    async def get_chat_administrators(self, chat: "Chat") -> list["ChatMember"] | None:
        """This service can be used to display admins of a group or channel.

        Parameters
        ----------
            chat: :class:`bale.Chat` 
                Group id
        Raises
        ------
            :class:`bale.Error`
        Returns
        -------
            Optional[List[:class:`bale.ChatMember`]]:
                list of chat member or ``None`` if chat not found.
        """
        if not isinstance(chat, Chat):
            raise TypeError(
                "chat param must be type of Chat"
            )

        response = await self.http.get_chat_administrators(chat.chat_id)
        return [ChatMember.from_dict(data=member_payload) for member_payload in response.result or list()]

    async def get_updates(self, offset: int = None, limit: int = None) -> list["Update"] | None:
        if offset and not isinstance(offset, int):
            raise TypeError(
                "offset param must be int"
            )

        if limit and not isinstance(limit, int):
            raise TypeError(
                "limit param must be int"
            )

        response = await self.http.get_updates(offset, limit)
        return [Update.from_dict(data=update_payload, bot=self) for update_payload in response.result or list() if not offset or (offset and update_payload.get("update_id") > offset)]

    async def connect(self):
        self._user = await self.get_bot()
        await self.updater.start()

    def run(self):
        """Run bot and https"""
        async def main():
            async with self:
                await self.connect()

        asyncio.run(main())
