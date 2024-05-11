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
from typing import Callable, Coroutine, Dict, Tuple, List, Union, Optional, Any, Set, TypeVar
from weakref import WeakValueDictionary

from bale import (
    WebhookInfo,
    State,
    Message,
    Update,
    User,
    MenuKeyboardMarkup,
    InlineKeyboardMarkup,
    Chat,
    LabeledPrice,
    ChatMember,
    Updater,
    PhotoSize,
    Document,
    Audio,
    Contact,
    Location,
    Video,
    Animation,
    Sticker
)
from bale.handlers import BaseHandler
from bale.checks import BaseCheck
from bale.request import HTTPClient
from ._waitcontext import WaitContext
from ._error import NotFound, InvalidToken
from .utils.types import CoroT, FileInput, MediaInput, STOP_UPDATER_MARKER, MissingValue
from .utils.logging import setup_logging
from .utils.files import parse_file_input
from .utils.params import arguments_shield
from .utils.request import handle_request_param

__all__ = ("Bot",)

_log = logging.getLogger(__name__)

class Bot:
    """This object represents a Bale Bot.

    Parameters
    ----------
        token: str 
            Bot’s unique authentication token. obtained via `@BotFather <https://ble.ir/BotFather>`_.

    All wrapped methods of Bale web services at a glance:

    .. tab:: Sending message

        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_animation`   | sending animation              |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_audio`       | sending audio                  |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_contact`     | sending contact                |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_document`    | sending document               |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_invoice`     | sending an invoice             |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_location`    | sending location               |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_media_group` | sending media grouped together |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_message`     | sending normal message         |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_photo`       | sending photo                  |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_sticker`     | sending sticker                |
        +-----------------------------------+--------------------------------+
        | :meth:`bale.Bot.send_video`       | sending video                  |
        +-----------------------------------+--------------------------------+

    .. tab:: Work with messages

        +---------------------------------------+----------------------------------------------+
        | :meth:`bale.Bot.copy_message`         | copying the contents of an arbitrary message |
        +---------------------------------------+----------------------------------------------+
        | :meth:`bale.Bot.delete_message`       | deleting message                             |
        +---------------------------------------+----------------------------------------------+
        | :meth:`bale.Bot.edit_message`         | editing message                              |
        +---------------------------------------+----------------------------------------------+
        | :meth:`bale.Bot.edit_message_caption` | editing captions                             |
        +---------------------------------------+----------------------------------------------+
        | :meth:`bale.Bot.forward_message`      | forwarding message                           |
        +---------------------------------------+----------------------------------------------+

    .. tab:: Get information

        +------------------------------+-------------------------------------+
        | :meth:`bale.Bot.get_chat`    | getting information about a chat    |
        +------------------------------+-------------------------------------+
        | :meth:`bale.Bot.get_me`      | getting information about bot       |
        +------------------------------+-------------------------------------+
        | :meth:`bale.Bot.get_message` | getting information about a message |
        +------------------------------+-------------------------------------+
        | :meth:`bale.Bot.get_user`    | getting information about a user    |
        +------------------------------+-------------------------------------+

    .. tab:: Update system

        +-----------------------------------+--------------------------------------+
        | :meth:`bale.Bot.delete_webhook`   | removing webhook integration         |
        +-----------------------------------+--------------------------------------+
        | :meth:`bale.Bot.set_webhook`      | setting a webhook to receive updates |
        +-----------------------------------+--------------------------------------+
        | :meth:`bale.Bot.get_updates`      | getting pending updates              |
        +-----------------------------------+--------------------------------------+
        | :meth:`bale.Bot.get_webhook_info` | getting current webhook status       |
        +-----------------------------------+--------------------------------------+

    .. tab:: Chat moderation and others

        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.ban_chat_member`         | banning a member from chat              |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.get_chat_administrators` | getting the list of admins in a chat    |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.leave_chat`              | leaving from a chat                     |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.get_chat_member`         | getting information about a chat member |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.get_chat_members_count`  | getting the number of members in a chat |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.invite_user`             | inviting a user to chat                 |
        +------------------------------------------+-----------------------------------------+
        | :meth:`bale.Bot.unban_chat_member`       | unbanning a user from chat              |
        +------------------------------------------+-----------------------------------------+

    .. admonition:: Examples

        :any:`My First Bot <examples.basic>`
    """
    __slots__ = (
        "token",
        "_events",
        "_waiters",
        "_handlers",
        "_state",
        "_client_user",
        "_http",
        "_closed",
        "__tasks",
        "update_queue",
        "updater"
    )

    def __init__(self, token: str, **kwargs):
        if not isinstance(token, str):
            raise InvalidToken()

        self.token: str = token
        self._http: HTTPClient = HTTPClient(token, **kwargs.pop('http_kwargs', {}))
        self._state: "State" = State(self, **kwargs.pop('state_kwargs', {}))
        self._client_user = None
        self._events: Dict[str, Callable] = {
            'on_event_error': self._on_event_error_callback,
            'on_handler_error': self._on_handler_error_callback
        }
        self._waiters: List[Tuple[Dict[Union[int, str], BaseCheck], asyncio.Future]] = []
        self._handlers: List[BaseHandler] = []
        self._closed: bool = True
        self.__tasks: Set[asyncio.Task] = set()
        self.update_queue: asyncio.Queue["Update" | STOP_UPDATER_MARKER] = asyncio.Queue()
        self.updater: Updater = Updater(self)

    @property
    def user(self) -> Optional["User"]:
        """:class:`bale.User`, optional: Represents the connected client. ``None`` if not logged in"""
        return self._client_user

    @property
    def state(self) -> Optional["State"]:
        """:class:`bale.State`, optional: Represents the state class for cache data. ``None`` if bot not logged in"""
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

    async def _setup_hook(self) -> None:
        self._closed = False
        await self._http.start()

    async def __aenter__(self):
        await self._setup_hook()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
        return None

    def listen(self, event_name: str) -> CoroT:
        """A decorator to set wrapper for an event.

        .. seealso::
            :any:`What is event? <events>`

        .. hint::
            .. code:: python

                @bot.listen("on_ready")
                async def ready_event_wrapper():
                    print(bot.user)

        Parameters
        ----------
            event_name: :obj:`str`
                Name of the event to set.
        """
        def wrapper_function(func) -> Any:
            self.add_event(event_name, func)

        return wrapper_function

    def handle(self, handler: "BaseHandler") -> CoroT:
        """A decorator to set callback for a handler.

        .. seealso::
            :any:`What is handler? <handlers>`

        .. important::
            The parameters of your wrapper function will vary depending on your handler.

        .. hint::
            .. code:: python

                from bale.handlers import MessageHandler

                ...

                @bot.handle(MessageHandler(...))
                async def message_handler_wrapper(message: bale.Message) -> None:
                    await message.reply("Cool!")

        Parameters
        ----------
            handler: :class:`bale.BaseHandler`
                a :class:`bale.BaseHandler` instance
        """
        def wrapper_function(func) -> Any:
            self.add_handler(handler, func)

        return wrapper_function

    def add_handler(self, handler: "BaseHandler", wrapper) -> None:
        """Set wrapper or listener for a handler.

        .. hint::
            .. code:: python

                from bale.handlers import MessageHandler

                ...
                async def message_handler_wrapper(message: bale.Message) -> None:
                    await message.reply("Cool!")

                bot.add_handler(MessageHandler(), message_handler_wrapper)

        Parameters
        ----------
            handler: :class:`bale.BaseHandler`
                a :class:`bale.BaseHandler` instance
            wrapper: Callable
                Function to add as wrapper for handler.
        """
        if not asyncio.iscoroutinefunction(wrapper):
            raise TypeError(f"{wrapper.__name__} is not a coroutine function")

        if not isinstance(handler, BaseHandler):
            raise TypeError('handler must be a BaseHandler instance')

        handler.set_callback(wrapper)
        self._handlers.append(handler)

    def add_event(self, event_name: str, wrapper) -> None:
        """Set wrapper or listener for an event.

        .. hint::
            .. code:: python

                ...
                async def ready_event_wrapper() -> None:
                    print(bot.user)

                bot.add_event('on_ready', ready_event_wrapper)

        Parameters
        ----------
            event_name: :obj:`str`
                Name of the event
            wrapper: Callable
                Function to add as wrapper for event
        """
        if not asyncio.iscoroutinefunction(wrapper):
            raise TypeError(f"{wrapper.__name__} is not a coroutine function")

        self._events[event_name] = wrapper

    def wait_for(self, checks: Union[Dict[Union[int, str], BaseCheck], List[BaseCheck], Tuple[BaseCheck], BaseCheck], timeout: Optional[float] = None):
        """Waits for a handler to be dispatched.

        This could be used to wait for a user to reply to a message, or send a photo, or to edit a message in a self-contained way.
        The timeout parameter is passed onto :meth:`asyncio.wait_for`. By default, it does not ``timeout``.
        Note that this does propagate the :class:`asyncio.TimeoutError` for you in case of timeout and is provided for ease of use.
        In case the event returns multiple arguments, a tuple containing those arguments is returned instead.

        .. important::
            This function returns the first check that meets the requirements.

        .. hint::
            To get better hints in the IDE, you should add a typehint to the result of this method.

            .. code:: python

                from bale import WaitContext

                ...
                ctx: WaitContext = await bot.wait_for(...)

        .. admonition:: Examples

            :any:`conversation Bot <examples.conversation>`

        Parameters
        ----------
            checks: Dict[:obj:`int` | :obj:`str`, :class:`bale.BaseCheck`] | :class:`bale.BaseCheck` | List[:class:`bale.BaseCheck`]
                The checks must be of the following types:

                - an instance of :class:`bale.BaseCheck` object
                    .. code:: python

                        from bale.checks import MessageId

                        ...
                        context = await bot.wait_for(MessageId(...), ...)

                - a list that contains the :class:`bale.BaseCheck` object
                    .. code:: python

                        from bale.checks import ATTACHMENT, MessageId, CAPTION

                        ...
                        context = await bot.wait_for([
                            ATTACHMENT, # message has any attachment (voice, audio, document, ...)
                            MessageId(1234), # The unique identifier of the message must be equal to "1234"
                            CAPTION  # message has any caption
                        ], ...)

                - a dict whose keys is types of :obj:`int` or :obj:`str` and it's values is types of instances of :class:`bale.BaseCheck` object
                    .. code:: python

                        from bale.checks import ATTACHMENT, MessageId, CAPTION

                        ...
                        context = await bot.wait_for({
                            1: ATTACHMENT, # message has any attachment (voice, audio, document, ...)
                            2: MessageId(1234), # The unique identifier of the message must be equal to "1234"
                            3: CAPTION  # message has any caption
                        }, ...)
                        if context.key == 1: # is the check key "1"?
                            await context.update.message.reply("you're sent a message with caption")

            timeout: :obj:`float`, optional
                The number of seconds to wait before timing out and raising :class:`asyncio.TimeoutError`.

                .. hint::
                    An example with use `timeout` argument:

                    .. code:: python

                        from bale.checks import MessageCheck

                        ...
                        try:
                            context = await bot.wait_for(MessageCheck(), timeout=20.0) # MessageCheck is a simple check to get a message
                        except asyncio.TimeoutError: # 20s A message with the conditions specified in the `checks` parameter was not found.
                            pass
        Raises
        ------
            asyncio.TimeoutError
                If a timeout is provided, and it was reached.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        if isinstance(checks, BaseCheck):
            checks: List[BaseCheck] = [checks]

        if isinstance(checks, (tuple, list)) and len(checks) > 0:
            _log.warning("Bot.wait_for: You have provided a list to the parameter “checks”;"
                         " we have converted it into a dictionary with numeric keys ranging from 0 to %s.\n"
                         "However, please use either the dictionary or a single BaseCheck instance in this parameter next time.", len(checks))
            checks: Dict[int, BaseCheck] = dict(zip(range(len(checks)), checks))

        if not isinstance(checks, dict):
            raise TypeError(
                "checks param must be type of BaseCheck instance or dict"
            )

        self._waiters.append((checks, future))
        return asyncio.wait_for(future, timeout=timeout)

    async def close(self):
        """Close http Events and bot"""
        if not self.is_closed():
            await self.update_queue.put(STOP_UPDATER_MARKER)
            await self.update_queue.join()

            await asyncio.gather(*self.__tasks)

            self._closed = True

            _log.info("Closing operation was successfully completed")

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
        except Exception as exc:
            try:
                self.dispatch('event_error', event_name, exc)
            except asyncio.CancelledError:
                pass

    def _create_event_schedule(self, core: CoroT, event_name: str, *args, **kwargs) -> asyncio.Task:
        task = self.run_event(core, event_name, *args, **kwargs)
        return self.create_task(task, name=f"Bot:process_event:{event_name}")

    def dispatch(self, event_name: str, /, *args, **kwargs) -> None:
        method = 'on_' + event_name
        core = self._events.get(method)
        if core:
            self._create_event_schedule(core, method, *args, **kwargs)

    async def _on_handler_error_callback(self, handler: "BaseHandler", update: "Update", exc: Exception):
        _log.exception('Exception in callback function of %s Ignored', handler.callback.__qualname__, exc_info=exc)

    async def _on_event_error_callback(self, event_name: str, exc):
        """an Event for get errors when exceptions"""
        _log.exception('Exception in %s Ignored', event_name, exc_info=exc)

    async def get_me(self) -> User:
        """Get bot information

        Returns
        -------
            :class:`bale.User`
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

    @arguments_shield
    async def set_webhook(self, url: str) -> bool:
        """Use this method to specify an url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, Bale will send an HTTPS POST request to the specified url, containing An Update.
        In case of an unsuccessful request, Bale will give up after a reasonable amount of attempts.

        .. code:: python

            await bot.set_webhook("https://example.com")

        Parameters
        ----------
            url: :obj:`str`
                HTTPS url to send updates to. Use an empty string to remove webhook integration.

        Returns
        -------
            :obj:`bool`:
                On success, :obj:`True` is returned.
        """
        response = await self._http.set_webhook(params=handle_request_param(dict(url=url)))
        return response.result or False

    @arguments_shield
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

    @arguments_shield
    async def send_message(self, chat_id: Union[str, int], text: str, *,
                           components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                           reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None) -> "Message":
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

        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_message(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
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
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }

        response = await self._http.forward_message(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        return result

    @arguments_shield
    async def send_document(self, chat_id: Union[str, int], document: Union["Document", FileInput], *,
                            caption: Optional[str] = MissingValue,
                            components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                            reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None,
                            file_name: Optional[str] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "document": parse_file_input(document, Document, file_name),
            "caption": caption,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_document(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_photo(self, chat_id: Union[str, int], photo: Union["PhotoSize", FileInput], *,
                         caption: Optional[str] = MissingValue,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                         reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[Union[str]] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "photo": parse_file_input(photo, PhotoSize, file_name),
            "caption": caption,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_photo(
            params=handle_request_param(payload)

        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_audio(self, chat_id: Union[str, int], audio: Union[Audio, FileInput], *,
                         caption: Optional[str] = MissingValue,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                         reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[str] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "audio": parse_file_input(audio, Audio, file_name),
            "caption": caption,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_audio(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_video(self, chat_id: Union[str, int], video: Union[Video, FileInput], *,
                         caption: Optional[str] = MissingValue,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                         reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None,
                         file_name: Optional[str] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "video": parse_file_input(video, Video, file_name),
            "caption": caption,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_video(params=handle_request_param(payload))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_animation(self, chat_id: Union[str, int], animation: Union[Animation, FileInput], *,
                             duration: Optional[int] = MissingValue, width: Optional[int] = MissingValue, height: Optional[int] = MissingValue,
                             caption: Optional[str] = MissingValue,
                             components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                             reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None,
                             file_name: Optional[str] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "animation": parse_file_input(animation, Animation, file_name),
            "duration": duration,
            "width": width,
            "height": height,
            "caption": caption,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_animation(params=handle_request_param(
            payload
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_media_group(self, chat_id: Union[str, int], media: List[MediaInput], *,
                             components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                             reply_to_message_id: Optional[Union[str, int]] = MissingValue) -> List["Message"]:
        """This service is used to send a group of photos, videos, documents or audios as an album.
        Documents and audio files can be only grouped on an album with messages of the same type.

        .. code:: python

            await bot.send_media_group(1234, [
                InputMediaPhoto("File ID", caption="example caption"),
                InputMediaPhoto("File ID"),
                InputMediaPhoto("File ID")
            ], ...)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            media: |media_input|
                Files to send.
            components: :class:`bale.InlineKeyboardMarkup` | :class:`bale.MenuKeyboardMarkup`, optional
                Message Components
            reply_to_message_id: :obj:`str` | :obj:`int`, optional
                |reply_to_message_id|

        Raises
        ------
            NotFound
                Invalid media.
            Forbidden
                You do not have permission to Send media group to chat.
            APIError
                Send media group Failed.
        """
        payload = {
            "chat_id": chat_id,
            "media": media,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_media_group(params=handle_request_param(
            payload
        ))
        messages = Message.from_list(payloads_list=response.result, bot=self)
        for msg in messages:
            self._state.store_message(msg)

        return messages

    @arguments_shield
    async def send_location(
            self, chat_id: Union[str, int], location: "Location",
            components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
            reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None
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
        payload = {
            "chat_id": chat_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "horizontal_accuracy": location.horizontal_accuracy,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self._http.send_location(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_contact(self, chat_id: Union[str, int], contact: "Contact",
                           components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = MissingValue,
                           reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "phone_number": contact.phone_number,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "reply_markup": components,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_contact(params=handle_request_param(payload))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def send_invoice(self, chat_id: Union[str, int], title: str, description: str, provider_token: str,
                           prices: List["LabeledPrice"], *,
                           invoice_payload: Optional[str] = None,
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
            invoice_payload: :obj:`str`, optional
                Bot-defined invoice payload. This will not be displayed to the user, use for your internal processes.
            photo_url: :obj:`str`, optional
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service.
                People like it better when they see what they are paying for.
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
        prices = [price.to_dict() for price in prices if isinstance(price, LabeledPrice)]
        payload = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "provider_token": provider_token,
            "prices": prices,
            "payload": invoice_payload,
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

    @arguments_shield
    async def send_sticker(self, chat_id: Union[str, int], sticker: Union["Sticker", FileInput], *,
                         reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send sticker.

        .. code:: python

            await bot.send_sticker(1234, "FILE ID", ...)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            sticker: :class:`bale.Sticker` | |file_input|
                Sticker file to send.
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
                You do not have permission to Send Sticker to chat.
            APIError
                Send sticker Failed.
        """
        payload = {
            "chat_id": chat_id,
            "sticker": parse_file_input(sticker, Sticker, None),
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.send_sticker(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
    async def edit_message(self, chat_id: Union[str, int], message_id: Union[str, int], text: str, *,
                           components: Optional["InlineKeyboardMarkup"] = MissingValue) -> "Message":
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
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": components
        }

        response = await self._http.edit_message_text(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(response.result, self)
        self._state.update_message(result)
        return result

    @arguments_shield
    async def edit_message_caption(self, chat_id: Union[str, int], message_id: Union[str, int], caption: str, *,
                           components: Optional["InlineKeyboardMarkup"] = MissingValue) -> "Message":
        """You can use this service to edit captions of messages that you have already sent through the arm.

        .. code:: python

            await bot.edit_message_caption(1234, 1234, "the message edited!", components=None)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            message_id: :obj:`str` | :obj:`int`
                Unique identifier for the message to edit.
            caption: :obj:`str`
                New caption of the message, 1-1024 characters after entities parsing.
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
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": caption,
            "reply_markup": components
        }

        response = await self._http.edit_message_caption(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(response.result, self)
        self._state.update_message(result)
        return result

    @arguments_shield
    async def copy_message(self, chat_id: Union[str, int], from_chat_id: Union[str, int], message_id: Union[str, int], *,
                           reply_to_message_id: Optional[Union[str, int]] = MissingValue, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """You can use this service to copy a message and send it in another chat.

        .. code:: python

            await bot.copy_message(1234, 1234, 1234)

        Parameters
        ----------
            chat_id: :obj:`str` | :obj:`int`
                |chat_id|
            from_chat_id: :obj:`str` | :obj:`int`
                Unique identifier for the chat where the original message was sent (or channel username in the format @channelusername).
            message_id: :obj:`str` | :obj:`int`
                Message identifier in the chat specified in from_chat_id.
            reply_to_message_id: :obj:`str` | :obj:`int`, optional
                |reply_to_message_id|
            delete_after: :obj:`float` | :obj:`int`, optional
                |delete_after|
        Raises
        ------
            NotFound
                Invalid Message or Chat ID.
            Forbidden
                You do not have permission to Copy or Send Message.
            APIError
                Copy Message Failed.
        """
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "reply_to_message_id": reply_to_message_id
        }

        response = await self._http.copy_message(
            params=handle_request_param(payload)
        )
        result = Message.from_dict(response.result, self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    @arguments_shield
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
        payload = {
            "chat_id": chat_id,
            "message_id": message_id
        }

        async def delete_message_task():
            if delay:
                await asyncio.sleep(delay)

            response = await self._http.delete_message(params=handle_request_param(payload))
            if response.result:
                self._state.remove_message(str(chat_id), message_id)

        if delay:
            await asyncio.create_task(delete_message_task())
        else:
            await delete_message_task()

    @arguments_shield
    async def get_chat(self, chat_id: Union[str, int], *, use_cache=True) -> Optional["Chat"]:
        """Use this method to get cashed or up-to-date information about the chat (current name of the user for one-on-one conversations,
        current username of a user, group or channel, etc.).

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

    @arguments_shield
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
        if use_cache and (founded_user := self._state.get_user(str(user_id))):
            return founded_user

        chat = await self.get_chat(user_id)

        if chat and chat.is_private_chat:
            result = User.from_dict(chat.to_dict(), self)
            self._state.store_user(result)
            return result

        self._state.remove_user(user_id)
        return None

    @arguments_shield
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
        return self._state.get_message(chat_id, message_id)

    @arguments_shield
    async def get_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Optional["ChatMember"]:
        """Use this method to get information about a member of a chat.
        The method is only guaranteed to work for other users if the bot is an administrator in the chat.

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
            :class:`bale.ChatMember`, optional
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

    @arguments_shield
    async def promote_chat_member(self,
          chat_id: Union[str, int],
          user_id: Union[str, int],
          can_be_edited: Optional[bool] = MissingValue,
          can_change_info: Optional[bool] = MissingValue,
          can_post_messages: Optional[bool] = MissingValue,
          can_edit_messages: Optional[bool] = MissingValue,
          can_delete_messages: Optional[bool] = MissingValue,
          can_invite_users: Optional[bool] = MissingValue,
          can_restrict_members: Optional[bool] = MissingValue,
          can_pin_messages: Optional[bool] = MissingValue,
          can_promote_members: Optional[bool] = MissingValue,
          can_send_messages: Optional[bool] = MissingValue,
          can_send_media_messages: Optional[bool] = MissingValue,
          can_reply_to_story: Optional[bool] = MissingValue,
          can_send_link_message: Optional[bool] = MissingValue,
          can_send_forwarded_message: Optional[bool] = MissingValue,
          can_see_members: Optional[bool] = MissingValue,
          can_add_story: Optional[bool] = MissingValue
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

    @arguments_shield
    async def ban_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> bool:
        """Use this method to ban a user from a group, supergroup or a channel. In the case of supergroups and channels,
        the user will not be able to return to the group on their own using invite links, etc., unless unbanned first.

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
        payload = {
            "chat_id": chat_id,
            "user_id": user_id
        }

        response = await self._http.ban_chat_member(
            params=handle_request_param(payload)
        )
        return response.result or False

    @arguments_shield
    async def unban_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int], *, only_if_banned: Optional[bool] = MissingValue) -> bool:
        """Use this method to unban a previously kicked user in a group or channel.
        The user will not return to the group or channel automatically, but will be able to join via link, etc.
        The bot must be an administrator for this to work. By default, this method guarantees that after the call the user is not a member of the chat,
        but will be able to join it. So if the user is a member of the chat they will also be removed from the chat.
        If you don’t want this, use the parameter only_if_banned.

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
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned
        }

        response = await self._http.ban_chat_member(
            params=handle_request_param(payload)
        )
        return response.result

    @arguments_shield
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

    @arguments_shield
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
            :obj:`int`
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

    @arguments_shield
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
        members = ChatMember.from_list(response.result, self)
        if members:
            for member in members:
                self._state.store_user(member.user)

        return members

    @arguments_shield
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

    @arguments_shield
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

    @arguments_shield
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

    @arguments_shield
    async def get_webhook_info(self) -> "WebhookInfo":
        """Use this method to get current webhook status.

        .. code:: python

            await bot.get_webhook_info()

        Returns
        -------
            :class:`bale.WebhookInfo`
                The webhook info.
        Raises
        ------
            APIError
                Get Webhook Info Failed.
        """
        response = await self._http.get_webhook_info()
        webhook_info = WebhookInfo.from_dict(response.result, bot=self)
        return webhook_info

    @arguments_shield
    async def get_updates(self, offset: Optional[int] = MissingValue, limit: Optional[int] = MissingValue) -> List["Update"]:
        """Use this method to get pending updates.

        .. code:: python

            updates = await bot.get_updates()

        Parameters
        ----------
            offset: :obj:`int`, optional
                Identifier of the first update to be returned. Must be greater by one than the highest among the identifiers of previously received updates.
            limit: :obj:`int`, optional
                Limits the number of updates to be retrieved. Values between `1`-`100` are accepted. Defaults to `100`.

        Raises
        ------
            Forbidden
                You do not have permission to get updates.
            APIError
                Get updates Failed.
        """
        payload = {
            "offset": offset,
            "limit": limit
        }

        response = await self._http.get_updates(
            params=handle_request_param(payload)
        )
        updates = [Update.from_dict(data=update_payload, bot=self) for update_payload in response.result
                if not offset or (offset and update_payload.get("update_id") > offset)] if response.result else None
        if updates:
            for update in updates:
                message = update.message
                callback = update.callback_query
                if message:
                    self._state.store_message(message)
                    if message.author:
                        self._state.store_user(message.author)
                if callback:
                    self._state.store_user(callback.user)

        return updates

    def done_task_callback(self, task: asyncio.Task) -> None:
        self.__tasks.discard(task)

    def create_task(self, coroutine: Coroutine, *, name: str = None) -> asyncio.Task:
        task = asyncio.create_task(coroutine, name=name)
        task.add_done_callback(self.done_task_callback)

        return task

    async def __run_handler(self, core: Coroutine, handler: "BaseHandler", update: "Update"):
        try:
            await core
        except asyncio.CancelledError:
            pass
        # except Exception as exc:
        #     try:
        #         self.dispatch('handler_error', handler, update, exc)
        #     except asyncio.CancelledError:
        #         pass
        # In Handler, errors are handled by their on_error function.

    async def _process_handler(self, handler: "BaseHandler", update: "Update", params: Tuple[Any, ...] = None):
        core = handler.handle_update(update, *params)
        await self.__run_handler(core, handler, update)

    async def process_update(self, update: "Update"):
        _log.debug("Processing update %s", update)
        self.dispatch('update', update)
        removed = []

        async def do_waiter(index, checks, future):
            if future.cancelled():
                removed.append(index)
                return

            for key, check in checks.items():
                is_correct = await check.check_update(update)
                if not is_correct:
                    continue

                waited_result = WaitContext(key, check, update)
                future.set_result(waited_result)
                removed.append(index)
                break

        for i, (checks_, future_) in enumerate(self._waiters):
            self.create_task(
                do_waiter(i, checks_, future_),
                name=f"Bot:do_waiter:{update.update_id}"
            )

        for item in reversed(removed):
            del self._waiters[item]

        async def do_handler(handler: "BaseHandler"):
            if (args := await handler.check_new_update(update)) is not None:
                await self._process_handler(handler, update, params=args),

        for _handler in self._handlers:
            self.create_task(
                do_handler(_handler),
                name=f"Bot:do_handler:{update.update_id}:{_handler}"
            )

    async def _process_update_wrapper(self, update: "Update"):
        await self.process_update(update)
        self.update_queue.task_done()

    async def __updater_fetcher(self) -> None:
        async def wrapper():
            while True:
                try:
                    item: Union["Update", STOP_UPDATER_MARKER] = await self.update_queue.get()
                    if item is STOP_UPDATER_MARKER:
                        while not self.update_queue.empty():
                            self.update_queue.task_done()

                        self.update_queue.task_done() # for the last item: STOP_UPDATER_MARKER
                        break

                    self.create_task(self._process_update_wrapper(item), name=f"Bot:updater_fetcher:process_update:{item.update_id}")
                except asyncio.CancelledError:
                    _log.warning("The update fetcher can only be closed with Bot.close.")

        self.create_task(wrapper(), name="Bot:updater_fetcher")

    def __run(self):
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(self._setup_hook())
            loop.run_until_complete(self.updater.setup())
            asyncio.ensure_future(self.__updater_fetcher())
            asyncio.ensure_future(self.updater.start_polling())
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            _log.debug("The request to stop receiving has been received. Currently in the process of shutting down...")
        except Exception as exc:
            _log.info("We encountered the error, currently in the process of shutting down...", exc_info=exc)
        finally:
            loop.run_until_complete(self.updater.stop())
            loop.run_until_complete(self.close())

    def run(self, /, log_handler: logging.Handler = None, log_level: int = logging.INFO, log_format: str = None):
        """This method is used to run the bot, updater, and update fetcher process.

        Parameters
        ----------
            log_handler: :class:`logging.Handler`, optional
                Your File. Pass a file_id as String to send a file that exists on the Bale servers (recommended),
                pass an HTTP URL as a String for Bale to get a file from the Internet, or upload a new one.
            log_level: :obj:`int`, optional
                Additional interface options. It is used only when uploading a file.
            log_format: :obj:`str`, optional
                Additional interface options. It is used only when uploading a file.

        """
        setup_logging(handler=log_handler, level=log_level, formatter=log_format)

        return self.__run()
