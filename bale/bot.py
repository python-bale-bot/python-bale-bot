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

import asyncio
import logging
from builtins import enumerate, reversed
from typing import Callable, Coroutine, Dict, Tuple, List, Union, Optional, overload
from weakref import WeakValueDictionary

from bale import (
    State, Message, Update, User, MenuKeyboardMarkup, InlineKeyboardMarkup,
    Chat, LabeledPrice, ChatMember, Updater, CallbackQuery,
    PhotoSize, Document, Audio, Contact, Location, Video, Animation
)
from bale.handlers import BaseHandler, CommandHandler, CallbackQueryHandler, MessageHandler
from bale.request import HTTPClient, handle_request_param
from .error import NotFound, InvalidToken
from .utils.types import CoroT, FileInput
from .utils.logging import setup_logging
from .utils.files import parse_file_input

__all__ = (
    "Bot"
)


_log = logging.getLogger(__name__)


class _Loop:
    __slots__ = ()

    def __getattr__(self, key):
        raise AttributeError((
            'loop attribute cannot be accessed in non-async contexts.'
        ))

_loop = _Loop()


class Bot:
    """This object represents a Bale Bot.

    Parameters
    ----------
        token: str 
            Bot’s unique authentication token. obtained via `@BotFather <https://ble.ir/BotFather>`_.

    .. attention::
        When you create a bot and run for first-step, use :meth:`bale.Bot.delete_webhook` method in `on_before_ready` event.
    .. admonition:: Examples

        :any:`My First Bot <examples.basic>`
    """
    __slots__ = (
        "loop",
        "token",
        "loop",
        "events",
        "listeners",
        "_handlers",
        "_state",
        "_client_user",
        "_http",
        "_closed",
        "updater"
    )

    def __init__(self, token: str, **kwargs):
        if not isinstance(token, str):
            raise InvalidToken()

        self.loop: Union[asyncio.AbstractEventLoop, _Loop] = _loop
        self.token: str = token
        self._http: HTTPClient = HTTPClient(self.loop, token, **kwargs.get('http_kwargs', {}))
        self._state: "State" = State(self, **kwargs.get('state_kwargs', {}))
        self._client_user = None
        self.events: Dict[str, List[Callable]] = {}
        self.listeners: List[Tuple[BaseHandler, asyncio.Future, Callable[["Update"], bool]]] = []
        self._handlers: List[BaseHandler] = []
        self._closed: bool = True

        self.updater: Updater = Updater(self)

    @property
    def user(self) -> Optional["User"]:
        """:class:`bale.User`, optional: Represents the connected client. ``None`` if not logged in"""
        return self._client_user

    @property
    def state(self) -> Optional["State"]:
        """:class:`bale.State`, options: Represents the state class for cache data. ``None`` if bot not logged in"""
        return self._state

    @property
    def cached_users(self) -> Optional[WeakValueDictionary[str, "User"]]:
        """:class:`weakref.WeakValueDictionary`[:obj:`str`, :class:`bale.User`]: Represents the users that the bot has ever encountered."""
        if self._state:
            return self._state.users
        return None

    @property
    def cached_chats(self) -> Optional[WeakValueDictionary[str, "Chat"]]:
        """:class:`weakref.WeakValueDictionary`[:obj:`str`, :class:`bale.Chat`]: Represents the chats that the bot has ever encountered."""
        if self._state:
            return self._state.chats
        return None

    async def _setup_hook(self):
        loop = asyncio.get_running_loop()
        self.loop = loop
        self._http.loop = loop
        self._closed = False
        await self._http.start()

    async def __aenter__(self):
        await self._setup_hook()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
        return None

    def event(self, coro: CoroT) -> CoroT:
        """Set wrapper or listener for selected event (the name of function).

        .. code:: python

            @bot.event
            async def on_message(message: bale.Message):
                ...

        .. hint::
            The name of the function for which you write the decorator is considered the name of the event.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event handler must be a coroutine function')

        self.add_event(coro.__name__, coro)
        return coro

    def listen(self, event_name: str) -> CoroT:
        """Set wrapper or listener for selected event (custom function name).

        .. code:: python

            @bot.listen("on_message")
            async def _message(message: bale.Message):
                ...

        Parameters
        ----------
            event_name: :obj:`str`
                Name of the event to set.
        """
        def wrapper_function(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('event handler must be coroutine function')

            self.add_event(event_name, func)

        return wrapper_function

    def handler(self, handler: object) -> CoroT:
        def wrapper_function(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('event handler must be coroutine function')

            self.add_handler(handler, func)

        return wrapper_function

    def add_handler(self, handler: object, wrapper):
        """Set wrapper or listener for an event.

        .. code:: python

            // must be complete

        Parameters
        ----------
            handler: :class:`object`
                Name of the event
            wrapper: Callable[]
                Function to add as wrapper for handler
        """
        if not asyncio.iscoroutinefunction(wrapper):
            raise TypeError(f"{wrapper.__name__} is not a Coroutine Function")

        if not isinstance(handler, BaseHandler):
            raise TypeError('handler must be BaseHandler or subclass of that')

        handler.set_callback(wrapper)
        self._handlers.append(handler)

    def add_event(self, event_name: str, wrapper):
        """Set wrapper or listener for an event.

        .. code:: python

            def message_handler(message: bale.Message):
                ...

            bot.add_event("on_message", message_handler)

        Parameters
        ----------
            event_name: :obj:`str`
                Name of the event
            wrapper: Callable[]
                Function to add as wrapper for event
        """
        if not asyncio.iscoroutinefunction(wrapper):
            raise TypeError(f"{wrapper.__name__} is not a Coroutine Function")

        if not self.events.get(event_name):
            self.events[event_name] = []

        self.events[event_name].append(wrapper)


    @overload
    async def wait_for(self, handler: "BaseHandler", *,
                       check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "Update":
        ...

    @overload
    async def wait_for(self, handler: "CallbackQueryHandler", *,
                       check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "CallbackQuery":
        ...

    @overload
    async def wait_for(self, handler: Union["MessageHandler", "CommandHandler"], *,
                       check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "Message":
        ...

    def wait_for(self, handler: BaseHandler, *, check: Optional[Callable[["Update"], bool]] = None,
                 timeout: Optional[float] = None):
        """Waits for an event to be dispatched.

        This could be used to wait for a user to reply to a message, or send a photo, or to edit a message in a self-contained way.
        The timeout parameter is passed onto asyncio.wait_for(). By default, it does not ``timeout``. Note that this does propagate the asyncio.TimeoutError for you in case of timeout and is provided for ease of use.
        In case the event returns multiple arguments, a tuple containing those arguments is returned instead.
        This function returns the first event that meets the requirements.

        .. code:: python

            message = await bot.wait_for(MessageHandler(check=lambda update: update.message.author.user_id == '1234'))
            ...
            try:
                message = await bot.wait_for(MessageHandler(), ..., timeout = 20.0)
            except asyncio.TimeoutError: # 20s A message with the conditions specified in the `check` parameter was not found.
                pass

        .. admonition:: Examples

            :any:`conversation Bot <examples.conversation>`

        Parameters
        ----------
            handler: :class:`bale.BaseHandler`
                A BaseHandler instance.
            check: Optional[Callable[..., :obj:`bool`]]
                A predicate to check what to wait for. The arguments must meet the parameters of the handler being waited for.
            timeout: Optional[:class:`float`]
                The number of seconds to wait before timing out and raising asyncio.TimeoutError.

        Raises
        ------
            asyncio.TimeoutError
                If a timeout is provided, and it was reached.
        """
        future = self.loop.create_future()
        if not check:
            check = lambda *args: True

        self.listeners.append((handler, future, check))
        return asyncio.wait_for(future, timeout=timeout)

    async def close(self):
        """Close http Events and bot"""
        await self.updater.stop()
        await self._http.close()
        self._closed = True

    def is_closed(self):
        """:obj:`bool`: Bot Status"""
        return self._closed

    def http_is_closed(self):
        """:obj:`bool`: HTTPClient Status"""
        return self._http.is_closed()

    async def run_event(self, core: CoroT, event_name: str, *args, **kwargs):
        try:
            await core(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as ext:
            await self.on_error(event_name, ext)

    def _create_event_schedule(self, core: CoroT, event_name: str, *args, **kwargs):
        task = self.run_event(core, event_name, *args, **kwargs)
        return self.loop.create_task(task, name=f"python-bale-bot:{event_name}")

    async def run_handler(self, core: Coroutine, handler: "BaseHandler", update: "Update"):
        try:
            await core
        except asyncio.CancelledError:
            pass
        except Exception as ext:
            await self.on_process_update_error(handler, update, ext)

    def _create_handler_schedule(self, handler: "BaseHandler", update: "Update", *args):
        core = handler.handle_update(update, *args)
        task = self.run_handler(core, handler, update)
        return self.loop.create_task(task, name=f"python-bale-bot:process_update:{handler}")

    def process_update(self, update: "Update"):
        self.dispatch('update', update)
        removed = []
        for index, (handler, future, check) in enumerate(self.listeners):
            args = handler.check_new_update(update)
            if not args or future.cancelled():
                removed.append(index)
                continue
            try:
                check_result = check(update)
            except Exception as _:
                future.set_exception(_)
                removed.append(index)
            else:
                if check_result:
                    if len(args) == 0:
                        future.set_result(None)
                    elif len(args) == 1:
                        future.set_result(args[0])
                    else:
                        future.set_result(args)
                    removed.append(index)

        for item in reversed(removed):
            del self.listeners[item]

        for handler in self._handlers:
            check = handler.check_new_update(update)
            if check is not None:
                self._create_handler_schedule(handler, update, *check)

    async def on_process_update_error(self, handler: "BaseHandler", update: "Update", error: Exception):
        _log.exception(f'Exception in callback function of {handler} Ignored')

    def dispatch(self, event_name: str, /, *args, **kwargs):
        method = 'on_' + event_name
        events_core = self.events.get(method)
        if events_core:
            for event_core in events_core:
                self._create_event_schedule(event_core, method, *args, **kwargs)

    async def on_error(self, event_name, error):
        """an Event for get errors when exceptions"""
        _log.exception(f'Exception in {event_name} Ignored')

    async def get_me(self) -> User:
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
        response = await self._http.get_me()
        client_user = User.from_dict(data=response.result, bot=self)
        self._client_user = client_user
        return client_user

    async def set_webhook(self, url: str) -> bool:
        """Use this method to specify an url and receive incoming updates via an outgoing webhook. Whenever there is an update for the bot, Bale will send an HTTPS POST request to the specified url, containing An Update. In case of an unsuccessful request, Bale will give up after a reasonable amount of attempts.

        .. code:: python

            await bot.set_webhook("https://example.com")

        Parameters
        ----------
            url: :obj:`str`
                HTTPS url to send updates to. Use an empty string to remove webhook integration.

        Returns
        -------
            :obj:`bool`:
                On success, True is returned.
        """
        response = await self._http.set_webhook(params=handle_request_param(dict(url=url)))
        return response.result or False

    async def delete_webhook(self) -> bool:
        """This service is used to remove the webhook set for the bot.

        .. code:: python

            await bot.delete_webhook()

        Returns
        -------
            :obj:`bool`:
                On success, True is returned.
        Raises
        ------
            Forbidden
                You do not have permission to delete Webhook.
            APIError
                Delete webhook Failed.
        """
        response = await self._http.delete_webhook()
        return response.result or False

    async def send_message(self, chat_id: Union[str, int], text: str, *,
                           components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                           reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send text messages.

        .. code:: python

            await bot.send_message(1234, "hi, python-bale-bot!", ...)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            text: :obj:`str`
                Text of the message to be sent. Max 4096 characters after entities parsing.
            components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
                Message Components
            reply_to_message_id: :obj:`str` | :obj:`int`, optional
                |reply_to_message_id|
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|

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
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of int or str"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        response = await self._http.send_message(
            params=handle_request_param(dict(chat_id=str(chat_id), text=text, reply_markup=components,
            reply_to_message_id=reply_to_message_id))
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def forward_message(self, chat_id: Union[str, int], from_chat_id: Union[str, int], message_id: Union[str, int]):
        """This service is used to send text messages.

        .. code:: python

            await bot.forward_message(1234, 1234, 1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            from_chat_id: :obj:`str` | :obj:`int`
                the chat where the original message was sent (or channel username in the format @channelusername).
            message_id: :obj:`str` | :obj:`int`
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

        response = await self._http.forward_message(
            params=handle_request_param(dict(chat_id=str(chat_id), from_chat_id=str(from_chat_id), message_id=str(message_id)))
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        return result

    async def send_document(self, chat_id: Union[str, int], document: Union["Document", FileInput], *,
                            caption: Optional[str] = None,
                            components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                            reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None,
                            file_name: Optional[str] = None) -> "Message":
        """This service is used to send document.

        .. code:: python

            await bot.send_document(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
        chat_id: :obj:`str` | :obj:`int`
            |chat_id|
        document: :class:`bale.Document` | |file_input|
            File to send.
        caption: :obj:`str`, optional
            Document caption.
        components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
            Message Components
        reply_to_message_id: :obj:`str` | :obj:`int`, optional
            |reply_to_message_id|
        delete_after: :obj:`float` | :obj:`int`, optional
            |delete_after|
        file_name: :obj:`str`, optional
            |file_name|

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

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        if file_name and not isinstance(file_name, str):
            raise TypeError(
                "file_name param must be type of str"
            )

        payload = {
            "chat_id": chat_id,
            "document": parse_file_input(document, Document, file_name)
        }
        if caption:
            payload["caption"] = caption
        if components:
            payload["reply_markup"] = components
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._http.send_document(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_photo(self, chat_id: Union[str, int], photo: Union["PhotoSize", FileInput], *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[Union[str]] = None) -> "Message":
        """This service is used to send photo.

        .. code:: python

            await bot.send_photo(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
        chat_id: :obj:`str` | :obj:`int`
            |chat_id|
        photo: :class:`bale.PhotoSize` | |file_input|
            File to send.
        caption: :obj:`str`, optional
            Photo caption.
        components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
            Message Components
        reply_to_message_id: :obj:`str` | :obj:`int`, optional
            |reply_to_message_id|
        delete_after: :obj:`float` | :obj:`int`, optional
            |delete_after|
        file_name: :obj:`str`, optional 
            |file_name|

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

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        if file_name and not isinstance(file_name, str):
            raise TypeError(
                "file_name param must be type of str"
            )

        payload = {
            "chat_id": chat_id,
            "photo": parse_file_input(photo, PhotoSize, file_name)
        }
        if caption:
            payload["caption"] = caption
        if components:
            payload["reply_markup"] = components
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._http.send_photo(
            params=handle_request_param(payload)

        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_audio(self, chat_id: Union[str, int], audio: Union[Audio, FileInput], *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[str] = None) -> "Message":
        """This service is used to send Audio.

        .. code:: python

            await bot.send_audio(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
        chat_id: :obj:`str` | :obj:`int`
            |chat_id|
        audio: :class:`bale.Audio` | |file_input|
            File to send.
        caption: :obj:`str`, optional
            Audio caption.
        components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
            Message Components
        reply_to_message_id: :obj:`str` | :obj:`int`, optional
            |reply_to_message_id|
        delete_after: :obj:`float` | :obj:`int`, optional
            |delete_after|
        file_name: :obj:`str`, optional
            |file_name|

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

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        if file_name and not isinstance(file_name, str):
            raise TypeError(
                "file_name param must be type of str"
            )

        payload = {
            "chat_id": chat_id,
            "audio": parse_file_input(audio, Audio, file_name)
        }
        if caption:
            payload["caption"] = caption
        if components:
            payload["reply_markup"] = components
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._http.send_audio(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_video(self, chat_id: Union[str, int], video: Union[Video, FileInput], *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[str] = None) -> "Message":
        """This service is used to send Video.

        .. code:: python

            await bot.send_video(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
        chat_id: :obj:`str` | :obj:`int`
            |chat_id|
        video: :class:`bale.Video` | |file_input|
            File to send.
        caption: :obj:`str`, optional
            Video caption.
        components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
            Message Components
        reply_to_message_id: :obj:`str` | :obj:`int`, optional
            |reply_to_message_id|
        delete_after: :obj:`float` | :obj:`int`, optional
            |delete_after|
        file_name: :obj:`str`, optional
            |file_name|

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

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        if file_name and not isinstance(file_name, str):
            raise TypeError(
                "file_name param must be type of str"
            )

        payload = {
            "chat_id": chat_id,
            "video": parse_file_input(video, Video, file_name)
        }
        if caption:
            payload["caption"] = caption
        if components:
            payload["reply_markup"] = components
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._http.send_video(params=handle_request_param(payload))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_animation(self, chat_id: Union[str, int], animation: Union[Animation, FileInput], *,
                             duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                             caption: Optional[str] = None,
                             components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                             reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None,
                             file_name: Optional[str] = None) -> "Message":
        """This service is used to send Animation.

        .. code:: python

            await bot.send_animation(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            animation: :class:`bale.Animation` | |file_input|
                File to send.
            duration: :obj:`int`, optional
                Duration of sent animation in seconds.
            width: :obj:`int`, optional
                Animation width.
            height: :obj:`int`, optional
                Animation height.
            caption: :obj:`str`, optional
                Animation caption.
            components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
                Message Components
            reply_to_message_id: :obj:`str` | :obj:`int`, optional 
                |reply_to_message_id|
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|
            file_name: :obj:`str`, optional
                |file_name|

        Returns
        --------
            :class:`bale.Message`
                The Message.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to Send Animation to chat.
            APIError
                Send Animation Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if duration and not isinstance(duration, int):
            raise TypeError(
                "duration param must be type of int"
            )

        if width and not isinstance(width, int):
            raise TypeError(
                "width param must be type of int"
            )

        if height and not isinstance(height, int):
            raise TypeError(
                "height param must be type of int"
            )

        if caption and not isinstance(caption, str):
            raise TypeError(
                "caption param must be type of str"
            )

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        if file_name and not isinstance(file_name, str):
            raise TypeError(
                "file_name param must be type of str"
            )

        payload = {
            "chat_id": chat_id,
            "animation": parse_file_input(animation, Animation, file_name)
        }
        if duration:
            payload["duration"] = duration
        if width:
            payload["width"] = width
        if height:
            payload["height"] = height
        if caption:
            payload["caption"] = caption
        if components:
            payload["reply_markup"] = components
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        response = await self._http.send_animation(params=handle_request_param(
            payload
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_location(
            self, chat_id: Union[str, int], location: "Location",
            components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
            reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None
    ) -> "Message":
        """Use this method to send point on the map.

        .. code:: python

            await bot.send_location(1234, bale.Location(35.71470468031143, 51.8568519168293))

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            location: :class:`bale.Location`
                The Location.
            components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
                Message Components
            reply_to_message_id: :obj:`str` | :obj:`int`
                |reply_to_message_id|
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|

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

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        response = await self._http.send_location(
            params=handle_request_param(
                dict(
                    chat_id=str(chat_id), latitude=location.latitude, longitude=location.longitude,
                    horizontal_accuracy=location.horizontal_accuracy, reply_markup=components,
                    reply_to_message_id=reply_to_message_id
                )
            )
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_contact(self, chat_id: Union[str, int], contact: "Contact",
                           components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                           reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send contact.

        .. code:: python

            await bot.send_cantact(1234, bale.Contact('09****', 'first name', 'last name'))

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                    |chat_id|
            contact: :class:`bale.Contact`
                The Contact.
            components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
                Message Components
            reply_to_message_id: :obj:`str` | :obj:`int`, optional
                |reply_to_message_id|
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|

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

        if not isinstance(contact, Contact):
            raise TypeError(
                "contact param must be type of Contact"
            )

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        if reply_to_message_id and not isinstance(reply_to_message_id, (str, int)):
            raise TypeError(
                "reply_to_message_id param must be type of str or int"
            )

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        response = await self._http.send_contact(params=handle_request_param(
            dict(
                chat_id=str(chat_id), phone_number=contact.phone_number, first_name=contact.first_name,
                last_name=contact.last_name, reply_markup=components,
                reply_to_message_id=reply_to_message_id
            )
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_invoice(self, chat_id: Union[str, int], title: str, description: str, provider_token: str,
                           prices: List["LabeledPrice"], *,
                           payload: Optional[str] = None,
                           photo_url: Optional[str] = None, need_name: Optional[bool] = False,
                           need_phone_number: Optional[bool] = False,
                           need_email: Optional[bool] = False, need_shipping_address: Optional[bool] = False,
                           is_flexible: Optional[bool] = True, delete_after: Optional[Union[float, int]] = None) -> Message:
        """You can use this service to send money request messages.

        .. important::
            When paying the amount, a fee will be charged from the sender.

        .. hint::
            The `on_successful_payment` event is called when the sent transaction is done.

        .. code:: python

            await bot.send_invoice(
                1234, "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                payload = "unique invoice payload", ...
            )

        .. admonition:: Examples

            :any:`Payment Bot <examples.invoice>`

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            title: :obj:`str`
                Product name. 1-32 characters.
            description: :obj:`str`
                Product description. 1-255 characters.
            provider_token: :obj:`str`
                You can use 3 methods to receive money:
                    1. Card number
                    2. Port number and acceptor number
                    3. Wallet number "Bale"
            prices: List[:class:`bale.LabeledPrice`]
                A list of prices.
            payload: :obj:`str`, optional
                Bot-defined invoice payload. This will not be displayed to the user, use for your internal processes.
            photo_url: :obj:`str`, optional
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.
            need_name: :obj:`bool`, optional
                Pass True, if you require the user’s full name to complete the order.
            need_phone_number: :obj:`bool`, optional
                Pass True, if you require the user’s phone number to complete the order.
            need_email: :obj:`bool`, optional
                Pass True, if you require the user’s email to complete the order.
            need_shipping_address: :obj:`bool`, optional
                Pass True, if you require the user’s shipping address to complete the order.
            is_flexible: :obj:`bool`, optional
                Pass True, if the final price depends on the shipping method.
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|

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

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        prices = [price.to_dict() for price in prices if isinstance(price, LabeledPrice)]
        payload = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "provider_token": provider_token,
            "prices": prices,
            "payload": payload,
            "photo_url": photo_url,
            "need_name": need_name,
            "need_phone_number": need_phone_number,
            "need_email": need_email,
            "need_shipping_address": need_shipping_address,
            "is_flexible": is_flexible
        }

        response = await self._http.send_invoice(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def edit_message(self, chat_id: Union[str, int], message_id: Union[str, int], text: str, *,
                           components: Optional["InlineKeyboardMarkup"] = None) -> "Message":
        """You can use this service to edit text messages that you have already sent through the arm.

        .. code:: python

            await bot.edit_message(1234, 1234, "the message edited!", components=None)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            message_id: :obj:`str` | :obj:`int`
                Unique identifier for the message to edit.
            text: :obj:`str`
                New text of the message, 1- 4096 characters after entities parsing.
            components: :class:`bale.InlineKeyboardMarkup`, optional
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

        if components:
            if not isinstance(components, (InlineKeyboardMarkup, MenuKeyboardMarkup)):
                raise TypeError(
                    "components param must be type of InlineKeyboardMarkup or MenuKeyboardMarkup"
                )
            components = components.to_json()

        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if components:
            payload["reply_markup"] = components
        response = await self._http.edit_message(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(response.result, self)
        self._state.update_message(result)
        return result

    async def delete_message(self, chat_id: Union[str, int], message_id: Union[str, int], *, delay: Optional[Union[int, float]] = None) -> None:
        """You can use this service to delete a message that you have already sent through the arm.

        .. code:: python

            await bot.delete_message(1234, 1234)

        .. warning::
            In channels or groups, only when the admin can delete other people's messages.
            Otherwise, It's no limit to delete his own message.

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            message_id: :obj:`str` | :obj:`int`
                Unique identifier for the message to delete.
            delay: :obj:`int` | :obj:`float`, optional
                If used, the message will be deleted after that number of seconds delay.
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

        if delay:
            if not isinstance(delay, (float, int)):
                raise TypeError(
                    "delay param must be type of float or int"
                )
            delay = float(delay)

        async def delete_message_task():
            if delay:
                await asyncio.sleep(delay)

            response = await self._http.delete_message(params=handle_request_param(dict(chat_id=str(chat_id), message_id=message_id)))
            if response.result:
                self._state.remove_message(str(chat_id), message_id)

        if delay:
            await asyncio.create_task(delete_message_task())
        else:
            await delete_message_task()

    async def get_chat(self, chat_id: Union[str, int], *, use_cache=True) -> Optional["Chat"]:
        """Use this method to get cashed or up-to-date information about the chat (current name of the user for one-on-one conversations, current username of a user, group or channel, etc.).

        .. code:: python

            await bot.get_chat(1234)
            ...
            await bot.get_chat("1234")

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                 |chat_id|
            use_cache: :obj:`bool`, optional
                 Use of caches stored in relation to chats.
        Returns
        -------
            :class:`bale.Chat` | None
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

        if use_cache and (founded_chat := self._state.get_chat(str(chat_id))):
            return founded_chat

        payload = {
            "chat_id" : str(chat_id)
        }

        try:
            response = await self._http.get_chat(
                params=handle_request_param(payload)
            )
        except NotFound:
            self._state.remove_chat(str(chat_id))
            return None
        else:
            chat = Chat.from_dict(response.result, bot=self)
            self._state.store_chat(chat)
            return chat

    async def get_user(self, user_id: Union[str, int], *, use_cache=True) -> Optional["User"]:
        """This Method almost like :meth:`bale.Bot.get_chat` , but this a filter that only get user.

        .. code:: python

            await bot.get_user(1234)
            ...
            await bot.get_user("1234")

        Parameters
        ----------
            user_id: :obj:`str` | :obj:`int`
                 Unique identifier for the target chat.
            use_cache: :obj:`bool`, optional
                Use of caches stored in relation to chats.
        Returns
        -------
            :class:`bale.User` | None
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

        if use_cache and (founded_user := self._state.get_user(str(user_id))):
            return founded_user

        chat = await self.get_chat(user_id)

        if chat and chat.is_private_chat:
            result = User.from_dict(chat.to_dict(), self)
            self._state.store_user(result)
            return result

        self._state.remove_user(user_id)
        return None

    async def get_message(self, chat_id: int, message_id: int) -> Optional["Message"]:
        """Use this method to get cashed information about the message.

        .. code:: python

            await bot.get_message(1234)

        Parameters
        ----------
            chat_id: :obj:`int`
                 |chat_id|
            message_id: :obj:`int`
                 Unique identifier for the target message.
        Returns
        -------
            :class:`bale.Message` | None
                The message or ``None`` if not found.
        """
        if not isinstance(chat_id, int):
            raise TypeError(
                "chat_id param must be type of int"
            )

        if not isinstance(message_id, int):
            raise TypeError(
                "message_id param must be type of int"
            )

        return self._state.get_message(chat_id, message_id)

    async def get_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Optional["ChatMember"]:
        """Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat.

        .. code:: python

            await bot.get_chat_member(1234, 1234)

        .. warning::
            Just only when the admin can ban member(s).

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            user_id: :obj:`str` | :obj:`int`
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

        payload = {
            "chat_id": chat_id,
            "user_id": user_id
        }

        try:
            response = await self._http.get_chat_member(
                params=handle_request_param(payload)
            )
        except NotFound:
            return None
        else:
            return ChatMember.from_dict(response.result, self)

    async def promote_chat_member(self,
          chat_id: Union[str, int],
          user_id: Union[str, int],
          can_be_edited: Optional[bool] = None,
          can_change_info: Optional[bool] = None,
          can_post_messages: Optional[bool] = None,
          can_edit_messages: Optional[bool] = None,
          can_delete_messages: Optional[bool] = None,
          can_invite_users: Optional[bool] = None,
          can_restrict_members: Optional[bool] = None,
          can_pin_messages: Optional[bool] = None,
          can_promote_members: Optional[bool] = None,
          can_send_messages: Optional[bool] = None,
          can_send_media_messages: Optional[bool] = None,
          can_reply_to_story: Optional[bool] = None,
          can_send_link_message: Optional[bool] = None,
          can_send_forwarded_message: Optional[bool] = None,
          can_see_members: Optional[bool] = None,
          can_add_story: Optional[bool] = None
    ):
        """an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass :obj:`False` for all boolean parameters to demote a user.

        .. code:: python

            await bot.promote_chat_member(1234, 1234, can_change_info = True)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            user_id: :obj:`str` | :obj:`int`
                Unique identifier of the target user.
            can_be_edited: :obj:`bool`, optional
                Pass :obj:`True`, if the bot is allowed to edit administrator privileges of that user.
            can_change_info: :obj:`bool`, optional
                Pass :obj:`True`, if the user can change the chat title, photo and other settings.
            can_post_messages: :obj:`bool`, optional
                Pass :obj:`True`, if the administrator can post messages in the channel,
                or access channel statistics; channels only.
            can_edit_messages: :obj:`bool`, optional
                Pass :obj:`True`,
                if the administrator can edit messages of other users and can pin messages; channels only.
            can_delete_messages: :obj:`bool`, optional
                Pass :obj:`True`, if the administrator can delete messages of other users.
            can_invite_users: :obj:`bool`, optional
                Pass :obj:`True`, if the user can invite new users to the chat.
            can_restrict_members: :obj:`bool`, optional
                Pass :obj:`True`, if the administrator can restrict, ban or unban chat members.
            can_pin_messages: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to pin messages, groups, channels only.
            can_promote_members: :obj:`bool`, optional
                Pass :obj:`True`,
                if the administrator can add new administrators with a subset of his own privileges or demote administrators
                that he has promoted, directly or indirectly (promoted by administrators that were appointed by the user).
            can_send_messages: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to send messages.
            can_send_media_messages: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to send a media message.
            can_reply_to_story: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to reply to a story.
            can_send_link_message: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to send a link message.
            can_send_forwarded_message: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to forward a message to chat.
            can_see_members: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to see the list of chat members.
            can_add_story: :obj:`bool`, optional
                Pass :obj:`True`, if the user is allowed to post a story from chat.

        Returns
        -------
            :obj:`bool`
                On success, ``True`` is returned.

        Raises
        ------
            NotFound
                Invalid Chat or User ID.
            Forbidden
                You do not have permission to promote Chat Member.
            APIError
                Promote chat member Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat param must be type of Chat"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        response = await self._http.get_chat_member(params=handle_request_param(dict(
            chat_id=str(chat_id),
            user_id=str(user_id),
            can_be_edited=can_be_edited,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
            can_send_messages=can_send_messages,
            can_send_media_messages=can_send_media_messages,
            can_reply_to_story=can_reply_to_story,
            can_send_link_message=can_send_link_message,
            can_send_forwarded_message=can_send_forwarded_message,
            can_see_members=can_see_members,
            can_add_story=can_add_story
        )))
        return response.result

    async def ban_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> bool:
        """Use this method to ban a user from a group, supergroup or a channel. In the case of supergroups and channels, the user will not be able to return to the group on their own using invite links, etc., unless unbanned first.

        .. code:: python

            await bot.ban_chat_member(1234, 1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            user_id: :obj:`str` | :obj:`int`
                Unique identifier of the target user.

        Returns
        -------
            :obj:`bool`
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

        payload = {
            "chat_id": chat_id,
            "user_id": user_id
        }

        response = await self._http.ban_chat_member(
            params=handle_request_param(payload)
        )
        return response.result or False

    async def unban_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int], *, only_if_banned: Optional[bool] = None) -> bool:
        """Use this method to unban a previously kicked user in a group or channel.
        The user will not return to the group or channel automatically, but will be able to join via link, etc. The bot must be an administrator for this to work. By default, this method guarantees that after the call the user is not a member of the chat, but will be able to join it. So if the user is a member of the chat they will also be removed from the chat. If you don’t want this, use the parameter only_if_banned.

        .. code:: python

            await bot.unban_chat_member(1234, 1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            user_id: :obj:`str` | :obj:`int`
                Unique identifier of the target user.
            only_if_banned: :obj:`bool`, optional
                 Do nothing if the user is not banned.
        Returns
        -------
            :obj:`bool`
                On success, ``True`` is returned.

        Raises
        ------
            NotFound
                Invalid Chat or User ID.
            Forbidden
                You do not have permission to unban Chat Member.
            APIError
                unban chat member Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        if not isinstance(user_id, (str, int)):
            raise TypeError(
                "user_id must be type of str or int"
            )

        if only_if_banned and not isinstance(only_if_banned, bool):
            raise TypeError(
                "only_if_banned param must be type of bool"
            )

        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned
        }

        response = await self._http.ban_chat_member(
            params=handle_request_param(payload)
        )
        return response.result

    async def set_chat_photo(self, chat_id: Union[str, int], photo: Union[PhotoSize, FileInput]) -> bool:
        """Use this method to set a new profile photo for the chat.

        .. code:: python

            await bot.set_chat_photo(1234, bale.InputFile("FILE_ID"))

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            photo: :class:`bale.PhotoSize` | |file_input|
                New chat photo. visit :class:`bale.InputFile` to see more info.

        Returns
        --------
            :obj:`bool`:
                On success, True is returned.

        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to Set Chat Photo to chat.
            APIError
                Set chat photo Failed.
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        payload = {
            "chat_id": chat_id,
            "photo": photo
        }

        response = await self._http.set_chat_photo(
            params=handle_request_param(payload)
        )
        return response.result or False

    async def get_chat_members_count(self, chat_id: Union[str, int]) -> int:
        """Use this method to get the number of members in a chat.

        .. code:: python

            await bot.get_chat_members_count(1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|

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
            :obj:`int`:
                The members count of the chat
        """
        if not isinstance(chat_id, (str, int)):
            raise TypeError(
                "chat_id param must be type of str or int"
            )

        payload = {
            "chat_id": chat_id
        }

        response = await self._http.get_chat_members_count(
            params=handle_request_param(payload)
        )
        return response.result

    async def get_chat_administrators(self, chat_id: Union[str, int]) -> Optional[List["ChatMember"]]:
        """Use this method to get a list of administrators in a chat.

        .. code:: python

            await bot.get_chat_administrators(1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
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

        payload = {
            "chat_id": chat_id
        }

        response = await self._http.get_chat_administrators(
            params=handle_request_param(payload)
        )
        result = [ChatMember.from_dict(data=member_payload, bot=self) for member_payload in response.result or list()]
        for member in result:
            self._state.store_user(member.user)

        return result

    async def get_file(self, file_id: str):
        """Use this method to get basic info about a file and prepare it for downloading. For the moment, bots can download files of up to ``20`` MB in size.

        .. code:: python

            await bot.get_file("FILE_ID")

        Parameters
        ----------
            file_id: :obj:`str`
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

        return await self._http.get_file(file_id)

    async def invite_user(self, chat_id: Union[str, int], user_id: Union[str, int]) -> bool:
        """Invite user to the chat

        .. code:: python

            await bot.get_chat(1234, 1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            user_id: :obj:`str` | :obj:`int`
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

        payload = {
            "chat_id": chat_id,
            "user_id": user_id
        }

        response = await self._http.invite_user(
            params=handle_request_param(payload)
        )
        return response.result or False

    async def leave_chat(self, chat_id: Union[str, int]) -> bool:
        """Use this method for your bot to leave a group, channel.

        .. code:: python

            await bot.leave_chat(1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|

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

        payload = {
            "chat_id": chat_id
        }

        response = await self._http.leave_chat(
            params=handle_request_param(payload)
        )

        if response.result:
            self._state.remove_chat(chat_id)
        return response.result or False

    async def get_updates(self, offset: Optional[int] = None, limit: Optional[int] = None) -> List["Update"]:
        if offset and not isinstance(offset, int):
            raise TypeError(
                "offset param must be int"
            )

        if limit and not isinstance(limit, int):
            raise TypeError(
                "limit param must be int"
            )

        payload = {}
        if offset:
            payload["offset"] = offset
        if limit:
            payload["limit"] = limit

        response = await self._http.get_updates(
            params=handle_request_param(payload)
        )
        result = [Update.from_dict(data=update_payload, bot=self) for update_payload in response.result
                if not offset or (offset and update_payload.get("update_id") > offset)] if response.result else None
        if result:
            for update in result:
                message = update.message
                callback = update.callback_query
                if message:
                    self._state.store_message(message)
                    if message.author:
                        self._state.store_user(message.author)

                if callback:
                    self._state.store_user(callback.user)

        return result

    async def connect(self):
        await self.get_me()
        await self.updater.start()

    def run(self):
        """Starting the bot, updater and HTTPClient."""

        async def main():
            async with self:
                await self.connect()

        setup_logging()
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass
