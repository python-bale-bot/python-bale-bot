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
import asyncio
from typing import Callable, Dict, Tuple, List, Optional
from builtins import enumerate, reversed
from .error import NotFound, InvalidToken
from bale import (Message, Update, User, Components, RemoveMenuKeyboard, Chat, Price, ChatMember, HTTPClient, Updater,
                  Photo, Document, Location, ContactMessage, Video, Audio, InputFile)

__all__ = (
    "Bot"
)


class _Loop:
    __slots__ = ()

    def __getattr__(self, key):
        raise AttributeError((
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
            'using asynchronous initialisation hooks such as Bot.setup_hook'
        ))

_loop = _Loop()


class Bot:
    """This object represents a Bale Bot.

    Parameters
    ----------
        token: str 
            Bot Token
        updater: Optional[:class:`bale.Updater`]

    .. note::
        When you create bot and run for first-step, use :meth:`bale.Bot.delete_webhook` method in `on_ready` event.
    """
    __slots__ = (
        "loop",
        "token",
        "loop",
        "events",
        "listeners",
        "_user",
        "http",
        "_closed",
        "updater"
    )

    def __init__(self, token: str, **kwargs):
        if not isinstance(token, str):
            raise InvalidToken()
        self.loop = _loop
        self.token = token
        self.http: HTTPClient = HTTPClient(self.loop, token)
        self._user = None
        self.events: Dict[str, List[Callable]] = {}
        self.listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self._closed = False

        self.updater: Updater = kwargs.get("updater", Updater)(self)

    def listen(self, event_name):
        """Register a Event"""
        return lambda func: self.add_event(event_name, func)

    def add_event(self, event: str, function):
        """Register an Event with event name"""
        if not asyncio.iscoroutinefunction(function):
            raise TypeError(f"{function.__name__} is not a Coroutine Function")

        if not self.events.get(event):
            self.events[event] = list()

        self.events[event].append(function)

    def remove_event(self, event: str, function=None):
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

    def wait_for(self, event_name: str, *, check=None, timeout=None):
        """Wait for an event"""
        self.loop: asyncio.AbstractEventLoop
        future = self.loop.create_future()
        event_name = event_name.lower()
        if not check:
            check = lambda *args: True

        listeners = self.listeners.get(event_name)
        if not listeners:
            listeners = []
            self.listeners[event_name] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout=timeout)

    @property
    def user(self) -> Optional["User"]:
        """Optional[:class:`bale.User`]: Represents the connected client. ``None`` if not logged in"""
        return self._user

    async def setup_hook(self):
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        await self.http.start()

    async def __aenter__(self):
        await self.setup_hook()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def close(self):
        """Close http Events and bot"""
        await self.http.close()
        await self.updater.stop()
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
        return self.loop.create_task(task, name=f"python-bale-bot: {event_name}")

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
            :class:`bale.User` :
                Bot User information.
        Raises
        ------
            APIError
                Get bot Failed.
        """
        response = await self.http.get_bot()
        return User.from_dict(data=response.result, bot=self)

    async def delete_webhook(self) -> bool:
        """This service is used to remove the webhook set for the bot.

        Returns
        -------
            bool:
                ``True`` else ``False`` if not done
        Raises
        ------
            Forbidden
                You do not have permission to delete Webhook.
            APIError
                Delete webhook Failed.
        """
        response = await self.http.delete_webhook()
        return response.result or False

    async def send_message(self, chat_id: str | int, text: str, *,
                           components: Optional["Components" | "RemoveMenuKeyboard"] = None,
                           reply_to_message_id: Optional[str | int] = None) -> "Message":
        """This service is used to send text messages.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            text: :class:`str`
                Text of the message to be sent. Max 4096 characters after entities parsing.
            components: Optional[:class:`bale.Components` | :class:`bale.RemoveComponents`]
                Message Components
            reply_to_message_id: Optional[:class:`str` | :class:`int`]
                If the message is a reply, ID of the original message.
        Returns
        -------
            :class:`bale.Message`
                The Message
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Message to this chat.
            APIError
                Send Message Failed.   
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if components:
            if not isinstance(components, (Components, RemoveMenuKeyboard)):
                raise TypeError(
                    "components param must be type of Components or RemoveComponents"
                )
            components = components.to_dict()

        if reply_to_message_id and not isinstance(reply_to_message_id, (int, str)):
            raise TypeError(
                "reply_to_message_id param must be type of Message"
            )

        response = await self.http.send_message(str(chat_id), text, components=components,
                                                reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def forward_message(self, chat_id: int | str, from_chat_id: int | str, message_id: int | str):
        """This service is used to send text messages.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            from_chat_id: :class:`str` | :class:`int`
                the chat where the original message was sent (or channel username in the format @channelusername).
            message_id: :class:`int` | :class:`str`
                Message in the chat specified in ``from_chat_id``.
        Returns
        -------
            :class:`bale.Message`
                The Message
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Message to this chat.
            APIError
                Forward Message Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(from_chat_id, (str, int)):
            raise TypeError(
                "from_chat_id param must be type of str or int"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )

        response = await self.http.forward_message(str(chat_id), str(from_chat_id), str(message_id))
        return Message.from_dict(data=response.result, bot=self)

    async def send_document(self, chat_id: str | int, document: "InputFile", *,
                            caption: Optional[str] = None,
                            reply_to_message_id: Optional[str | int] = None) -> "Message":
        """This service is used to send document.

        .. warning::
            To upload a file, you must fill in the "file_name" param and end it with the file extension.

        Parameters
        ----------
        chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
        document: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
        caption: Optional[:class:`str`]
                Document caption.
        reply_to_message_id: Optional[:class:`str` | :class:`int`]
                If the message is a reply, ID of the original message.

        Returns
        --------
            :class:`bale.Message`
                The Message.
                
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Document to this chat.
            APIError
                Send Document Failed.        
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(document, InputFile):
            raise TypeError(
                "document param must be type of InputFile"
            )

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.send_document(chat_id, [document.to_dict('document')], caption=caption,
                                                 reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_photo(self, chat_id: str | int, photo: "InputFile", *,
                         caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        """This service is used to send photo.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            photo: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Photo caption.
            reply_to_message_id: Optional[:class:`str` | :class:`int`]
                If the message is a reply, ID of the original message.

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to Send Photo to chat.
            APIError
                Send photo Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(photo, InputFile):
            raise TypeError(
                "photo param must be type of InputFile"
            )

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.send_photo(str(chat_id), [photo.to_dict('photo')], caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_audio(self, chat_id: str | int, audio: "InputFile", *,
                         caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        """This service is used to send Audio.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            audio: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Audio caption.
            reply_to_message_id: Optional[:class:`str` | :class:`int`]
                If the message is a reply, ID of the original message.

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to Send Audio to chat.
            APIError
                Send Audio Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(audio, InputFile):
            raise TypeError(
                "audio param must be type of InputFile"
            )

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.send_audio(str(chat_id), [audio.to_dict('audio')], caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_video(self, chat_id: str | int, video: "InputFile", *,
                         caption: Optional[str] = None,
                         reply_to_message_id: Optional[str | int] = None) -> "Message":
        """This service is used to send Video.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            video: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Video caption.
            reply_to_message_id: Optional[:class:`str` | :class:`int`]
                If the message is a reply, ID of the original message.

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to Send Video to chat.
            APIError
                Send Video Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(video, InputFile):
            raise TypeError(
                "video param must be type of bytes, str or Video"
            )

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        response = await self.http.send_video(str(chat_id), [video.to_dict('video')], caption=caption,
                                              reply_to_message_id=reply_to_message_id)
        return Message.from_dict(data=response.result, bot=self)

    async def send_location(self, chat_id: str | int, location: "Location") -> "Message":
        """Use this method to send point on the map.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            location: :class:`bale.Location`
                The Location.

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Location to this chat.
            APIError
                Send Location Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(location, Location):
            raise TypeError(
                "location param must be type of Location"
            )

        response = await self.http.send_location(str(chat_id), location.latitude, location.longitude)
        return Message.from_dict(data=response.result, bot=self)

    async def send_contact(self, chat_id: str | int, contact: "ContactMessage") -> "Message":
        """This service is used to send contact.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                    Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            contact: :class:`bale.ContactMessage`
                The Contact.

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Contact Message to this chat.
            APIError
                Send Contact Message Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of str or int"
            )

        if not isinstance(contact, ContactMessage):
            raise TypeError(
                "contact param must be type of ContactMessage"
            )

        response = await self.http.send_contact(str(chat_id), contact.phone_number, contact.first_name,
                                                last_name=contact.last_name)
        return Message.from_dict(data=response.result, bot=self)

    async def send_invoice(self, chat_id: str | int, title: str, description: str, provider_token: str,
                           prices: List["Price"], *,
                           payload: Optional[str] = None,
                           photo_url: Optional[str] = None, need_name: Optional[bool] = False,
                           need_phone_number: Optional[bool] = False,
                           need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False,
                           is_flexible: Optional[bool] = True) -> Message:
        """You can use this service to send money request messages.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                    Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            title: str
                Product name. 1- 32 characters.
            description: str
                Product description. 1- 255 characters.
            provider_token: str
                You can use 3 methods to receive money: 1.Card number 2. Port number and acceptor number 3. Wallet number "Bale"
            prices: List[:class:`bale.Price`]
                A list of prices.
            payload: Optional[:class:`str`]
                Bot-defined invoice payload. This will not be displayed to the user, use for your internal processes.
            photo_url: Optional[:class:`str`]
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.
            need_name: Optional[bool]
                Pass True, if you require the user’s full name to complete the order.
            need_phone_number: Optional[bool]
                Pass True, if you require the user’s phone number to complete the order.
            need_email: Optional[bool]
                Pass True, if you require the user’s email to complete the order.
            need_shipping_address: Optional[bool]
                Pass True, if you require the user’s shipping address to complete the order.
            is_flexible: Optional[bool]
                Pass True, if the final price depends on the shipping method.

        Returns
        -------
            :class:`bale.Message`
            
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Invoice to this chat.
            APIError
                Send Invoice Failed.  
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of str or int"
            )

        if not isinstance(title, str):
            raise TypeError(
                "title param must be type of str"
            )

        if not isinstance(provider_token, str):
            raise TypeError(
                "provider_token param must be type of str"
            )

        if not isinstance(prices, list):
            raise TypeError(
                "prices must param must be type of list"
            )

        if payload and not isinstance(payload, str):
            raise TypeError(
                "payload param must be type of str"
            )

        if photo_url and not isinstance(photo_url, str):
            raise TypeError(
                "photo_url param must be type of str"
            )

        if need_name is not None and not isinstance(need_name, bool):
            raise TypeError(
                "need_name param must be type of boolean"
            )

        if need_phone_number is not None and not isinstance(need_phone_number, bool):
            raise TypeError(
                "need_phone_number param must be type of boolean"
            )

        if need_email is not None and not isinstance(need_email, bool):
            raise TypeError(
                "need_email param must be type of boolean"
            )

        if need_shipping_address is not None and not isinstance(need_shipping_address, bool):
            raise TypeError(
                "need_shipping_address param must be type of boolean"
            )

        if is_flexible is not None and not isinstance(is_flexible, bool):
            raise TypeError(
                "is_flexible param must be type of boolean"
            )

        prices = [price.to_dict() for price in prices if isinstance(price, Price)]
        response = await self.http.send_invoice(str(chat_id), title, description, provider_token, prices, payload, photo_url,
                                                need_name,
                                                need_phone_number, need_email, need_shipping_address, is_flexible)
        return Message.from_dict(data=response.result, bot=self)

    async def edit_message(self, chat_id: str | int, message_id: str | int, text: str, *,
                           components: Optional["Components" | "RemoveMenuKeyboard"] = None) -> "Message":
        """You can use this service to edit text messages that you have already sent through the arm.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            message_id: :class:`str` | :class:`int`
                Unique identifier for the message to edit.
            text: str
                New text of the message, 1- 4096 characters after entities parsing.
            components: Optional[:class:`bale.Components` | :class:`bale.RemoveComponents`]
                An object for an inline keyboard.
        Raises
        ------
            NotFound
                Invalid Message or Chat ID.
            Forbidden
                You do not have permission to Edit Message.
            APIError
                Edit Message Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )

        if components and not isinstance(components, (Components, RemoveMenuKeyboard)):
            raise TypeError(
                "components param must be type of Components or RemoveComponents"
            )

        if components:
            components = components.to_dict()

        response = await self.http.edit_message(chat_id, message_id, text, components=components)
        return response.result

    async def delete_message(self, chat_id: str | int, message_id: str | int) -> bool:
        """You can use this service to delete a message that you have already sent through the arm.

        .. warning::
            In Channel or Group:
                If it is a group or channel Manager, it can delete a message from (group or channel).

            In private message (PV):
                If the message was sent by a bot, it can be deleted with this method

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            message_id: :class:`bale.Message`
                Unique identifier for the message to delete.
        Raises
        ------
            NotFound
                Invalid Message or Chat ID.
            Forbidden
                You do not have permission to Delete Message.
            APIError
                Delete Message Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(message_id, (str, int)):
            raise TypeError(
                "message_id param must be type of str or int"
            )
        response = await self.http.delete_message(str(chat_id), message_id)
        return response.result or False

    async def get_chat(self, chat_id: int | str) -> Chat | None:
        """Use this method to get up-to-date information about the chat (current name of the user for one-on-one conversations, current username of a user, group or channel, etc.).

        Parameters
        ----------
            chat_id: int | str
                 Unique identifier for the target chat or username of the target channel (in the format @channelusername).
        Returns
        -------
            Optional[:class:`bale.Chat`]
                The chat or ``None`` if not found.
        Raises
        ------
            Forbidden
                You do not have permission to get Chat.
            APIError
                Get chat Failed.
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
        Returns
        -------
            Optional[:class:`bale.User`]
                The user or ``None`` if not found.
        Raises
        ------
            Forbidden
                You do not have permission to get User.
            APIError
                Get user Failed.
        """
        if not isinstance(user_id, (int, str)):
            raise TypeError(
                "user_id param must be type of int or str"
            )

        chat = await self.get_chat(user_id)
        if chat and chat.parsed_type.is_private_chat:
            return User.from_dict(chat.to_dict(), self)

        return None

    async def get_chat_member(self, chat_id: str | int, user_id: str | int) -> "ChatMember" | None:
        """Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: Optional[:class:`int` | :class:`str`]
                Unique identifier of the target user.

        Returns
        -------
            Optional[:class:`bale.ChatMember`]
                The chat member of ``None`` if not found.

        Raises
        ------
            NotFound
                Invalid Chat or User ID.
            Forbidden
                You do not have permission to get Chat Member.
            APIError
                Get chat member Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of Chat"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        try:
            response = await self.http.get_chat_member(chat_id=str(chat_id), member_id=str(user_id))
        except NotFound:
            return None
        else:
            return ChatMember.from_dict(chat_id, response.result, self)

    async def ban_chat_member(self, chat_id: str | int, user_id: str | int) -> "ChatMember":
        """Use this method to ban a user from a group, supergroup or a channel. In the case of supergroups and channels, the user will not be able to return to the group on their own using invite links, etc., unless unbanned first.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: :class:`int` | :class:`str`
                Unique identifier of the target user.

        Returns
        -------
            :class:`bool`
                On success, ``True`` is returned.

        Raises
        ------
            NotFound
                Invalid Chat or User ID.
            Forbidden
                You do not have permission to ban Chat Member.
            APIError
                ban chat member Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        response = await self.http.ban_chat_member(chat_id=str(chat_id), member_id=str(user_id))
        return response.result

    async def get_chat_members_count(self, chat_id: str | int) -> int:
        """Use this method to get the number of members in a chat.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to get Members count of the Chat.
            APIError
                get Members count of the Chat Failed.

        Returns
        --------
            :class:`int`:
                The members count of the chat
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        response = await self.http.get_chat_members_count(str(chat_id))
        return response.result

    async def get_chat_administrators(self, chat_id: str | int) -> list["ChatMember"] | None:
        """Use this method to get a list of administrators in a chat.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
        Returns
        -------
            List[:class:`bale.ChatMember`]
                list of chat member.
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to get Administrators of the Chat.
            APIError
                get Administrators of the Chat from chat Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        response = await self.http.get_chat_administrators(chat_id)
        return [ChatMember.from_dict(chat_id=chat_id, data=member_payload, bot=self) for member_payload in response.result or list()]

    async def get_file(self, file_id: str):
        """Use this method to get basic info about a file and prepare it for downloading. For the moment, bots can download files of up to ``20`` MB in size.

        Parameters
        ----------
            file_id: :class:`str`
                Either the file identifier to get file information about.

        Returns
        -------
            :class:`bytes`
                The content of the file

        Raises
        ------
            NotFound
                Invalid file ID.
            Forbidden
                You do not have permission to download File.
            APIError
                download File Failed.
        """
        if not isinstance(file_id, str):
            raise TypeError(
                "file_id must be type of str"
            )

        return await self.http.get_file(file_id)

    async def invite_user(self, chat_id: str | int, user_id: str | int) -> bool:
        """Invite user to the chat

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: :class:`str` | :class:`int`
                Unique identifier for the target user.

        Raises
        ------
            NotFound
                Invalid Chat or User ID.
            Forbidden
                You do not have permission to Add user to Chat.
            APIError
                Invite user Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id param must be type of str or int"
            )

        response = await self.http.invite_to_chat(str(chat_id), str(user_id))
        return response.result or False

    async def leave_chat(self, chat_id: str | int) -> bool:
        """Use this method for your bot to leave a group, channel.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).

        Raises
        ------
            Forbidden
                You do not have permission to Leave from chat.
            APIError
                Leave from chat Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )
        response = await self.http.leave_chat(str(chat_id))
        return response.result or False

    async def get_updates(self, offset: int = None, limit: int = None) -> list["Update"]:
        if offset and not isinstance(offset, int):
            raise TypeError(
                "offset param must be int"
            )

        if limit and not isinstance(limit, int):
            raise TypeError(
                "limit param must be int"
            )

        response = await self.http.get_updates(offset, limit)
        return [Update.from_dict(data=update_payload, bot=self) for update_payload in response.result
                if not offset or (offset and update_payload.get("update_id") > offset)] if response.result else None

    async def connect(self, sleep_after_every_get_updates):
        self._user = await self.get_bot()
        await self.updater.start(sleep_after_every_get_updates=sleep_after_every_get_updates)

    def run(self, sleep_after_every_get_updates=None):
        """Run bot and https"""

        async def main():
            async with self:
                await self.connect(sleep_after_every_get_updates=sleep_after_every_get_updates)

        try:
            asyncio.run(main())
        except KeyboardInterrupt:  # Control-C
            pass
        except SystemExit:
            pass
