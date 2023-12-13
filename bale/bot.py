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
import logging
from typing import Callable, Dict, Tuple, List, Union, Optional, overload, Literal
from builtins import enumerate, reversed
from .error import NotFound, InvalidToken
from .utils import setup_logging, CoroT
from bale import (State, Message, Update, User, MenuKeyboardMarkup, InlineKeyboardMarkup, Chat, Price, ChatMember, Updater,
                  Location, ContactMessage, InputFile, CallbackQuery, SuccessfulPayment)
from bale.request import HTTPClient, handle_request_param

__all__ = (
    "Bot"
)


_log = logging.getLogger(__name__)


class _Loop:
    __slots__ = ()

    def __getattr__(self, key):
        raise AttributeError((
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
        ))

_loop = _Loop()


class Bot:
    """This object represents a Bale Bot.

    Parameters
    ----------
        token: str 
            Bot Token

    .. attention::
        When you create bot and run for first-step, use :meth:`bale.Bot.delete_webhook` method in `on_before_ready` event.
    .. admonition:: Examples

        :any:`My First Bot <examples.basic>`
    """
    __slots__ = (
        "loop",
        "token",
        "loop",
        "events",
        "listeners",
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
        self._state: "State" = State(self, **kwargs)
        self._client_user = None
        self.events: Dict[str, List[Callable]] = {}
        self.listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self._closed: bool = True

        self.updater: Updater = Updater(self)

    @property
    def user(self) -> Optional["User"]:
        """Optional[:class:`bale.User`]: Represents the connected client. ``None`` if not logged in"""
        return self._client_user

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
        return

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

        self._add_event(coro.__name__, coro)
        return coro

    def listen(self, event_name: str) -> CoroT:
        """Set wrapper or listener for selected event (custom function name).

        .. code:: python

            @bot.listen("on_message")
            async def _message(message: bale.Message):
                ...

        Parameters
        ----------
            event_name: :class:`str`
                Name of the event to set.
        """
        def wrapper_function(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('event handler must be coroutine function')

            self._add_event(event_name, func)

        return wrapper_function

    def _add_event(self, event_name: str, wrapper):
        """Set wrapper or listener for an event.

        .. code:: python

            def message_handler(message: bale.Message):
                ...

            bot.add_event("on_message", message_handler)

        Parameters
        ----------
            event_name: :class:`str`
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
    async def wait_for(self, event_name: Literal['update'], *,
                       check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "Update":
        ...

    @overload
    async def wait_for(self, event_name: Literal['callback_query'], *, check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "CallbackQuery":
        ...

    @overload
    async def wait_for(self, event_name: Literal['message', 'edit_message'], *, check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "Message":
        ...

    @overload
    async def wait_for(self, event_name: Literal['member_chat_join', 'member_chat_leave'], *, check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> Tuple["Message", "Chat", "User"]:
        ...

    @overload
    async def wait_for(self, event_name: Literal['successful_payment'], *, check: Optional[Callable[..., bool]] = None,
                       timeout: Optional[float] = None) -> "SuccessfulPayment":
        ...

    def wait_for(self, event_name: str, *, check: Optional[Callable[..., bool]]=None, timeout: Optional[float]=None):
        """Waits for an event to be dispatched.

        This could be used to wait for a user to reply to a message, or send a photo, or to edit a message in a self-contained way.
        The timeout parameter is passed onto asyncio.wait_for(). By default, it does not ``timeout``. Note that this does propagate the asyncio.TimeoutError for you in case of timeout and is provided for ease of use.
        In case the event returns multiple arguments, a tuple containing those arguments is returned instead.
        This function returns the first event that meets the requirements.

        .. code:: python

            message = await bot.wait_for("message", check = lambda m: m.author.user_id == '1234')
            ...
            try:
                message = await bot.wait_for("message", ..., timeout = 20.0)
            except asyncio.TimeoutError: # 20s A message with the conditions specified in the `check` parameter was not found.
                pass

        .. admonition:: Examples

            :any:`conversation Bot <examples.conversation>`

        Parameters
        ----------
            event_name: :class:`str`
                Name of the event
            check: Optional[Callable[..., :class:`bool`]]
                A predicate to check what to wait for. The arguments must meet the parameters of the event being waited for.
            timeout: Optional[:class:`float`]
                The number of seconds to wait before timing out and raising asyncio.TimeoutError.

        Raises
        ------
            asyncio.TimeoutError
                If a timeout is provided, and it was reached.
        """
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

    async def close(self):
        """Close http Events and bot"""
        await self.updater.stop()
        await self._http.close()
        self._closed = True

    def is_closed(self):
        """:class:`bool`: Bot Status"""
        return self._closed

    def http_is_closed(self):
        """:class:`bool`: HTTPClient Status"""
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
        return self.loop.create_task(task, name=f"python-bale-bot: {event_name}")

    def dispatch(self, event_name: str, /, *args, **kwargs):
        method = 'on_' + event_name
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
                self._create_event_schedule(event_core, method, *args, **kwargs)

    async def on_error(self, event_name, error):
        """a Event for get errors when exceptions"""
        _log.exception(f'Exception in {event_name} Ignored')

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
        response = await self._http.get_bot()
        client_user = User.from_dict(data=response.result, bot=self)
        self._client_user = client_user
        return client_user

    async def set_webhook(self, url: str) -> bool:
        """Use this method to specify an url and receive incoming updates via an outgoing webhook. Whenever there is an update for the bot, Bale will send an HTTPS POST request to the specified url, containing An Update. In case of an unsuccessful request, Bale will give up after a reasonable amount of attempts.

        .. code:: python

            await bot.set_webhook("https://example.com")

        Parameters
        ----------
            url: :class:`str`
                HTTPS url to send updates to. Use an empty string to remove webhook integration.

        Returns
        -------
            :class:`bool`:
                On success, True is returned.
        """
        response = await self._http.set_webhook(params=handle_request_param(dict(url=url)))
        return response or False

    async def delete_webhook(self) -> bool:
        """This service is used to remove the webhook set for the bot.

        .. code:: python

            await bot.delete_webhook()

        Returns
        -------
            :class:`bool`:
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
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            text: :class:`str`
                Text of the message to be sent. Max 4096 characters after entities parsing.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
            reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        if reply_to_message_id and not isinstance(reply_to_message_id, (int, str)):
            raise TypeError(
                "reply_to_message_id param must be type of Message"
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
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            from_chat_id: Union[:class:`str`, :class:`int`]
                the chat where the original message was sent (or channel username in the format @channelusername).
            message_id: Union[:class:`int`, :class:`str`]
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

    async def send_document(self, chat_id: Union[str, int], document: "InputFile", *,
                            caption: Optional[str] = None,
                            components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                            reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send document.

        .. code:: python

            await bot.send_document(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
        chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
        document: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
        caption: Optional[:class:`str`]
                Document caption.
        components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
        reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
        delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        response = await self._http.send_document(
            params=handle_request_param(
                dict(
                    chat_id=chat_id, caption=caption, reply_markup=components,
                    reply_to_message_id=reply_to_message_id
                ),
                [document.to_multipart_payload('document')]
            )
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_photo(self, chat_id: Union[str, int], photo: "InputFile", *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send photo.

        .. code:: python

            await bot.send_photo(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            photo: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Photo caption.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
            reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        response = await self._http.send_photo(
            params=handle_request_param(
                dict(
                    chat_id=str(chat_id), caption=caption, reply_markup=components,
                    reply_to_message_id=reply_to_message_id
                ),
                [photo.to_multipart_payload('photo')]
            )

        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_audio(self, chat_id: Union[str, int], audio: "InputFile", *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send Audio.

        .. code:: python

            await bot.send_audio(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            audio: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Audio caption.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
            reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        response = await self._http.send_audio(params=handle_request_param(
            dict(
                chat_id=str(chat_id), caption=caption, reply_markup=components,
                reply_to_message_id=reply_to_message_id),
            [audio.to_multipart_payload('audio')]
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_video(self, chat_id: Union[str, int], video: "InputFile", *,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send Video.

        .. code:: python

            await bot.send_video(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            video: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            caption: Optional[:class:`str`]
                Video caption.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
            reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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
                "video param must be type of InputFile"
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

        response = await self._http.send_video(params=handle_request_param(
              dict(
                    chat_id=str(chat_id), caption=caption, reply_markup=components,
                    reply_to_message_id=reply_to_message_id
              ),
              [video.to_multipart_payload('video')]
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_animation(self, chat_id: Union[str, int], animation: "InputFile", *,
                         duration: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None,
                         caption: Optional[str] = None,
                         components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None,
                         reply_to_message_id: Optional[Union[str, int]] = None, delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send Animation.

        .. code:: python

            await bot.send_animation(1234, bale.InputFile("FILE_ID"), caption = "this is a caption", ...)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            animation: :class:`bale.InputFile`
                File to send. visit :class:`bale.InputFile` to see more info.
            duration: :class:`int`
                Duration of sent animation in seconds.
            width: :class:`int`
                Animation width.
            height: :class:`int`
                Animation height.
            caption: Optional[:class:`str`]
                Animation caption.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
                Message Components
            reply_to_message_id: Optional[Union[:class:`str`, :class:`int`]]
                If the message is a reply, ID of the original message.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        if not isinstance(animation, InputFile):
            raise TypeError(
                "animation param must be type of InputFile"
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

        response = await self._http.send_animation(params=handle_request_param(
            dict(
                chat_id=str(chat_id), duration=duration,
                width=width, height=height,
                caption=caption,
                reply_markup=components,
                reply_to_message_id=reply_to_message_id
            ),
            [animation.to_multipart_payload('animation')]
        ))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_location(self, chat_id: Union[str, int], location: "Location", delete_after: Optional[Union[float, int]] = None) -> "Message":
        """Use this method to send point on the map.

        .. code:: python

            await bot.send_location(1234, bale.Location(35.71470468031143, 51.8568519168293))

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            location: :class:`bale.Location`
                The Location.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        response = await self._http.send_location(params=handle_request_param(dict(chat_id=str(chat_id), latitude=location.latitude, longitude=location.longitude)))
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_contact(self, chat_id: Union[str, int], contact: "ContactMessage", delete_after: Optional[Union[float, int]] = None) -> "Message":
        """This service is used to send contact.

        .. code:: python

            await bot.send_cantact(1234, bale.ContactMessage('09****', 'first name', 'last name'))

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                    Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            contact: :class:`bale.ContactMessage`
                The Contact.
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        if delete_after and not isinstance(delete_after, (int, float)):
            raise TypeError(
                "delete_after param must be type of int or float"
            )

        response = await self._http.send_contact(params=handle_request_param(
            dict(
                chat_id=str(chat_id), phone_number=contact.phone_number, first_name=contact.first_name,
                last_name=contact.last_name)
            )
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def send_invoice(self, chat_id: Union[str, int], title: str, description: str, provider_token: str,
                           prices: List["Price"], *,
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
                1234, "invoice title", "invoice description", "6037************", [bale.Price("label", 2000)],
                payload = "unique invoice payload", ...
            )

        .. admonition:: Examples

            :any:`Payment Bot <examples.invoice>`

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
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
            delete_after: Optional[Union[:class:`float`, :class:`int`]]
                If used, the sent message will be deleted after the specified number of seconds.

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

        prices = [price.to_dict() for price in prices if isinstance(price, Price)]
        response = await self._http.send_invoice(
            params=handle_request_param(dict(chat_id=str(chat_id), title=title, description=description, provider_token=provider_token, prices=prices, payload=payload, photo_url=photo_url,
            need_name=need_name, need_phone_number=need_phone_number, need_email=need_email, need_shipping_address=need_shipping_address, is_flexible=is_flexible))
        )
        result = Message.from_dict(data=response.result, bot=self)
        self._state.store_message(result)
        if delete_after:
            await self.delete_message(result.chat_id, result.message_id, delay=delete_after)

        return result

    async def edit_message(self, chat_id: Union[str, int], message_id: Union[str, int], text: str, *,
                           components: Optional[Union["InlineKeyboardMarkup", "MenuKeyboardMarkup"]] = None) -> "Message":
        """You can use this service to edit text messages that you have already sent through the arm.

        .. code:: python

            await bot.edit_message(1234, 1234, "this is tested", components=None)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            message_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the message to edit.
            text: str
                New text of the message, 1- 4096 characters after entities parsing.
            components: Optional[Union[:class:`bale.InlineKeyboardMarkup`, :class:`bale.MenuKeyboardMarkup`]]
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

        response = await self._http.edit_message(params=handle_request_param(dict(chat_id=chat_id, message_id=message_id, text=text, reply_markup=components)))
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
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            message_id: :class:`bale.Message`
                Unique identifier for the message to delete.
            delay: Optional[Union[:class:`int`, :class:`float`]]
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

        async def delete_message_task(d: Optional[float] = None):
            if d:
                await asyncio.sleep(d)

            response = await self._http.delete_message(params=handle_request_param(dict(chat_id=str(chat_id), message_id=message_id)))
            if response.result:
                self._state.remove_message(str(chat_id), message_id)

        if delay:
            await asyncio.create_task(delete_message_task(delay))
        else:
            await delete_message_task()

    async def get_chat(self, chat_id: Union[str, int], *, use_cache=True) -> Optional["Chat"]:
        """Use this method to get up-to-date information about the chat (current name of the user for one-on-one conversations, current username of a user, group or channel, etc.).

        .. code:: python

            await bot.get_chat(1234)
            ...
            await bot.get_chat("1234")

        Parameters
        ----------
            chat_id: Union[:class:`int`, :class:`str`]
                 Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            use_cache: Optional[:class:`bool`]
                 Use of caches stored in relation to chats.
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

        if use_cache:
            result = self._state.get_chat(chat_id)
            if result:
                return result

        try:
            response = await self._http.get_chat(params=handle_request_param(dict(chat_id=str(chat_id))))
        except NotFound:
            self._state.remove_chat(str(chat_id))
            return None
        else:
            chat = Chat.from_dict(response.result, bot=self)
            self._state.store_chat(chat)
            return chat

    async def get_user(self, user_id: Union[str, int], *, use_cache=True) -> Optional["User"]:
        """This Method almost like :class:`bale.Bot.get_chat` , but this a filter that only get user.

        .. code:: python

            await bot.get_user(1234)
            ...
            await bot.get_user("1234")

        Parameters
        ----------
            user_id: Union[:class:`int`, :class:`str`]
                 Unique identifier for the target chat.
            use_cache: Optional[:class:`bool`]
                Use of caches stored in relation to chats.
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

        if use_cache:
            result = self._state.get_user(user_id)
            if result:
                return result

        chat = await self.get_chat(user_id)
        if chat and chat.parsed_type.is_private_chat:
            payload = {
                "username": chat.username,
                "id": chat.chat_id,
                "first_name": chat.first_name,
                "last_name": chat.last_name
            }
            result = User.from_dict(payload, self)
            self._state.store_user(result)
            return result

        self._state.remove_user(user_id)
        return None

    async def get_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Optional["ChatMember"]:
        """Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat.

        .. code:: python

            await bot.get_chat_member(1234, 1234)

        .. warning::
            Just only when the admin can ban member(s).

        Parameters
        ----------
            chat_id: Union[:class:`int`, :class:`str`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: Union[:class:`int`, :class:`str`]
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
            response = await self._http.get_chat_member(params=handle_request_param(dict(chat_id=str(chat_id), member_id=str(user_id))))
        except NotFound:
            return None
        else:
            return ChatMember.from_dict(chat_id, response.result, self)

    async def ban_chat_member(self, chat_id: Union[str, int], user_id: Union[str, int]) -> "ChatMember":
        """Use this method to ban a user from a group, supergroup or a channel. In the case of supergroups and channels, the user will not be able to return to the group on their own using invite links, etc., unless unbanned first.

        .. code:: python

            await bot.ban_chat_member(1234, 1234)

        Parameters
        ----------
            chat_id: Union[:class:`int`, :class:`str`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: Union[:class:`int`, :class:`str`]
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

        response = await self._http.ban_chat_member(params=handle_request_param(dict(chat_id=str(chat_id), member_id=str(user_id))))
        return response.result

    async def get_chat_members_count(self, chat_id: Union[str, int]) -> int:
        """Use this method to get the number of members in a chat.

        .. code:: python

            await bot.get_chat_members_count(1234)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
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

        response = await self._http.get_chat_members_count(params=handle_request_param(dict(chat_id=str(chat_id))))
        return response.result

    async def get_chat_administrators(self, chat_id: Union[str, int]) -> Optional[List["ChatMember"]]:
        """Use this method to get a list of administrators in a chat.

        .. code:: python

            await bot.get_chat_administrators(1234)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
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

        response = await self._http.get_chat_administrators(params=handle_request_param(dict(chat_id=str(chat_id))))
        result = [ChatMember.from_dict(chat_id=chat_id, data=member_payload, bot=self) for member_payload in response.result or list()]
        for member in result:
            self._state.store_user(member.user)

        return result

    async def get_file(self, file_id: str):
        """Use this method to get basic info about a file and prepare it for downloading. For the moment, bots can download files of up to ``20`` MB in size.

        .. code:: python

            await bot.get_file("FILE_ID")

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

        return await self._http.get_file(file_id)

    async def invite_user(self, chat_id: Union[str, int], user_id: Union[str, int]) -> bool:
        """Invite user to the chat

        .. code:: python

            await bot.get_chat(1234, 1234)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            user_id: Union[:class:`str`, :class:`int`]
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

        response = await self._http.invite_to_chat(params = handle_request_param(dict(chat_id=str(chat_id), user_id=str(user_id))))
        return response.result or False

    async def leave_chat(self, chat_id: Union[str, int]) -> bool:
        """Use this method for your bot to leave a group, channel.

        .. code:: python

            await bot.leave_chat(1234)

        Parameters
        ----------
            chat_id: Union[:class:`str`, :class:`int`]
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
        response = await self._http.leave_chat(params=handle_request_param(dict(chat_id=str(chat_id))))
        if response.result:
            self._state.remove_chat(chat_id)
        return response.result or False

    async def get_updates(self, offset: int = None, limit: int = None) -> List["Update"]:
        if offset and not isinstance(offset, int):
            raise TypeError(
                "offset param must be int"
            )

        if limit and not isinstance(limit, int):
            raise TypeError(
                "limit param must be int"
            )

        response = await self._http.get_updates(params=handle_request_param(dict(offset=offset, limit=limit)))
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
        await self.get_bot()
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
