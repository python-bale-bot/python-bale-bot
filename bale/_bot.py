#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

import asyncio
import io
import logging
import platform
import sys
import warnings
from collections.abc import Callable, Coroutine
from contextlib import suppress
from pathlib import Path
from typing import (TYPE_CHECKING, Any, Literal, Type, TypeAlias, TypedDict,
                    TypeVar, cast, overload)

import aiohttp

from ._chatfullinfo import ChatFullInfo
from ._chatinvitelink import ChatInviteLink
from ._chatmember import ChatMember
from ._exceptions import (FlowBadStatusError, MiddlewareError, NotFound,
                          RateLimited)
from ._message import Message
from ._request import BaleResponse, HTTPClient, Route
from ._sticker import Sticker
from ._transaction import Transaction
from ._update import Update
from ._user import User
from ._utils import request as utils_request
from ._utils import token as _token
from ._utils.checkers import (check_subclass, iscoroutinefunction,
                              validate_storage)
from ._utils.files import parse_file_input
from ._utils.logging import setup_logging
from ._utils.typehint import MISSING, CoroT, SentinelOrValue
from ._utils.typehint_manager import arguments_shield
from ._webhookinfo import WebhookInfo
from .attachments import (Animation, Audio, Contact, Document, InputFile,
                          InputMediaAnimation, InputMediaAudio,
                          InputMediaDocument, InputMediaPhoto, InputMediaVideo,
                          Location, PhotoSize, Video, Voice)
from .constants import (DEFAULT_GET_UPDATES_TIMEOUT, APIEndpoint,
                        ConversationFlowTarget)
from .context import Context
from .helpers import find as _find
from .updater import Updater

if TYPE_CHECKING:
    from bale import (InlineKeyboardMarkup, LabeledPrice, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove)

    from ._types.user import User as UserPayload
    from .flow import ConversationFlow
    from .handlers import UpdateHandler
    from .middleware import BaseMiddleware
    from .storage import BaseStorage

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

FileInput: TypeAlias = str | bytes | Path | InputFile
ReplyMarkupT: TypeAlias = (
    "InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove"
)

__all__ = ("Bot",)

_log = logging.getLogger(__name__)
HandlerT = TypeVar("HandlerT", bound="UpdateHandler")
FlowT = TypeVar("FlowT", bound="Type[ConversationFlow]")

MediaInput: TypeAlias = (
    InputMediaPhoto
    | InputMediaVideo
    | InputMediaAnimation
    | InputMediaAudio
    | InputMediaDocument
)
STOP_UPDATER_MARKER = object()


class BotOptions(TypedDict, total=False):
    connector_init: dict[str, Any] | None
    http_trace: aiohttp.TraceConfig | None
    proxy: str | None
    proxy_auth: aiohttp.BasicAuth | None
    storage: "BaseStorage | None"


class Bot:
    """This object represents a Bale Bot.

    Arguments:
        token:
            Bot’s unique authentication token. obtained via `@BotFather <https://ble.ir/BotFather>`_.
        connector_init: dict[:py:class:`str`, :py:data:`~typing.Any`]
            A dictionary that is passed to the parameters of the connector object (:class:`aiohttp.TCPConnector`) during its creation.
        proxy: :py:class:`str` | None
            The proxy address. It is used when creating a :class:`aiohttp.ClientSession` object.
        proxy_auth: :py:class:`~aiohttp.BasicAuth` | None
            An object that represents authentication in a proxy and is also used during the creation of a :class:`aiohttp.ClientSession` object.
        http_trace: :py:class:`~aiohttp.TraceConfig` | None
            Configuration for tracking the HTTP requests sent with the :mod:`aiohttp` library.
        storage: :py:class:`~bale.storage.BaseStorage` | None
            The storage backend used for persisting and managing data across four distinct levels:
            bot data, user data, chat data, and conversation data. It works in conjunction with
            :class:`~bale.storage.StorageConfig` to ensure configuration consistency and validate implemented
            methods against enabled data categories.

    An overview of all wrapped methods of the `Bale <https://ble.ir>`_ web services:

    .. tab:: Sending Messages

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.send_message`
              - sending normal message
            * - :meth:`~Bot.send_photo`
              - sending photo
            * - :meth:`~Bot.send_video`
              - sending video
            * - :meth:`~Bot.send_animation`
              - sending animation
            * - :meth:`~Bot.send_audio`
              - sending audio
            * - :meth:`~Bot.send_voice`
              - sending voice
            * - :meth:`~Bot.send_contact`
              - sending contact
            * - :meth:`~Bot.send_document`
              - sending document
            * - :meth:`~Bot.send_invoice`
              - sending an invoice
            * - :meth:`~Bot.send_location`
              - sending location
            * - :meth:`~Bot.send_sticker`
              - sending sticker
            * - :meth:`~Bot.send_chat_action`
              - sending chat action
            * - :meth:`~Bot.send_media_group`
              - sending media grouped together

    .. tab:: Message Management

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.copy_message`
              - copying the contents of an arbitrary message
            * - :meth:`~Bot.delete_message`
              - deleting message
            * - :meth:`~Bot.edit_message_text`
              - editing message (text)
            * - :meth:`~Bot.edit_message_caption`
              - editing captions
            * - :meth:`~Bot.edit_message_reply_markup`
              - editing reply markup
            * - :meth:`~Bot.forward_message`
              - forwarding message

    .. tab:: Retrieving Information

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.get_me`
              - getting information about bot
            * - :meth:`~Bot.get_chat`
              - getting information about a chat
            * - :meth:`~Bot.get_user`
              - getting information about a user
            * - :meth:`~Bot.get_chat_member`
              - getting information about a chat member
            * - :meth:`~Bot.get_chat_members`
              - getting the list of members in a chat

    .. tab:: Webhook & Update System

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.delete_webhook`
              - removing webhook integration
            * - :meth:`~Bot.set_webhook`
              - setting a webhook to receive updates
            * - :meth:`~Bot.get_updates`
              - getting pending updates
            * - :meth:`~Bot.get_webhook_info`
              - getting current webhook status

    .. tab:: Invite Links

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.create_chat_invite_link`
              - creating an invitation link for a chat
            * - :meth:`~Bot.export_chat_invite_link`
              - exporting the primary invite link of a chat
            * - :meth:`~Bot.revoke_chat_invite_link`
              - revoking an invitation link

    .. tab:: Chat Moderation & Utilities

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.leave_chat`
              - leaving from a chat
            * - :meth:`~Bot.invite_user`
              - inviting a user to chat
            * - :meth:`~Bot.get_chat_administrators`
              - getting the list of admins in a chat
            * - :meth:`~Bot.get_chat_members_count`
              - getting the number of members in a chat
            * - :meth:`~Bot.set_chat_title`
              - setting the title of a chat
            * - :meth:`~Bot.set_chat_photo`
              - setting the photo of a chat
            * - :meth:`~Bot.delete_chat_photo`
              - deleting the photo of a chat
            * - :meth:`~Bot.set_chat_description`
              - setting the description of a chat
            * - :meth:`~Bot.promote_chat_member`
              - promoting/demoting a chat member (admin rights)
            * - :meth:`~Bot.ban_chat_member`
              - banning a member from chat
            * - :meth:`~Bot.unban_chat_member`
              - unbanning a user from chat
            * - :meth:`~Bot.pin_chat_message`
              - pinning a message
            * - :meth:`~Bot.unpin_chat_message`
              - unpinning a message
            * - :meth:`~Bot.unpin_all_chat_messages`
              - unpinning all messages in a chat

    .. tab:: Payments

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.answer_pre_checkout_query`
              - answering a pre-checkout query
            * - :meth:`~Bot.create_invoice_link`
              - creating an invoice link
            * - :meth:`~Bot.inquire_transaction`
              - inquiring about a transaction
            * - :meth:`~Bot.ask_review`
              - asking for a review on a payment

    .. tab:: Callback & Files

        .. list-table::
            :widths: 40 60
            :header-rows: 1

            * - Method
              - Description
            * - :meth:`~Bot.answer_callback_query`
              - answering a callback query
            * - :meth:`~Bot.download_file`
              - downloading a file

    Note:
        The values provided for the parameters of any covered method are validated against their defined type hints before sending the request to the web service. If a value does not match the type hint, a :exc:`TypeError` will be raised.

    .. include:: bot_async_context_manager.rst

    .. admonition:: Examples

        :any:`My First Bot <examples.basic>`

    See Also:
        :ref:`how_to_create_bale_bot`

    .. versionchanged:: 3.0
        - The :paramref:`options` parameter has been added.
        - CamelCase aliases have been added for all bot methods to fully synchronize with the official naming conventions of the Bale documentation.
    """

    __slots__ = (
        "token",
        "update_queue",
        "_listeners",
        "_middlewares",
        "_waiters",
        "_handlers",
        "_registered_flows",
        "_flows",
        "_flows_lock",
        "_storage",
        "_client_user",
        "_http",
        "_closed",
        "_updater",
        "__tasks",
        "__updater_fetcher_task",
        "__ready_event",
    )

    def __init__(self, token: str, **options: Unpack[BotOptions]) -> None:
        _token.validate_token(token)

        self.token: str = token
        connector_init: dict[str, Any] | None = options.get("connector_init")
        http_trace: aiohttp.TraceConfig | None = options.get("http_trace")
        proxy: str | None = options.get("proxy")
        proxy_auth: aiohttp.BasicAuth | None = options.get("proxy_auth")
        storage: "BaseStorage | None" = options.get("storage")
        if storage is not None:
            validate_storage(storage)

        self.update_queue: asyncio.Queue[Update | Literal["STOP_UPDATER_MARKER"]] = (
            asyncio.Queue()
        )
        self._updater: Updater | None = Updater(self)
        self._http: HTTPClient = HTTPClient(
            token,
            connector_init=connector_init,
            http_trace=http_trace,
            proxy=proxy,
            proxy_auth=proxy_auth,
        )
        self._storage: "BaseStorage | None" = storage
        self._client_user = None
        self._listeners: dict[str, list[Callable]] = {}
        self._middlewares: list["BaseMiddleware"] = []

        self._registered_flows: set[Type["ConversationFlow"]] = set()
        self._flows: set["ConversationFlow"] = set()
        self._flows_lock: asyncio.Lock = asyncio.Lock()

        self._handlers: list["UpdateHandler"] = []
        self._closed: bool = True
        self.__tasks: set[asyncio.Task] = set()
        self.__updater_fetcher_task: asyncio.Task[None] | None = None
        self.__ready_event: asyncio.Event | None = None

    @property
    def bot_id(self) -> int | None:
        """The unique identifier of the bot. If the bot has started, it is extracted from the cached response of the :meth:`get_me` method; otherwise, it is extracted from the :paramref:`Bot.token`."""
        if user := self.user:
            return user.id
        return _token.extract_bot_id(self.token)

    @property
    def user(self) -> "User | None":
        """The bot account information, represented as an instance of bale.User.
        This property holds the value :obj:`None` until the bot is fully operational and the bot account information is retrieved from the web service.

        Important:
            Upon successful execution of the bot or every time the :meth:`get_me` method is manually called, this property’s information is automatically updated.

        Hint:
            To prevent runtime errors caused by the initial value of this property (:obj:`None`), it is recommended to use this value only within handlers and events from `on_ready <events.html#on_ready>`_ onwards, or to use the :meth:`wait_for_ready` helper method before accessing it.

        See Also:
            :meth:`run`
            :meth:`get_me`
            :meth:`wait_for_ready`
        """
        return self._client_user

    @property
    def storage(self) -> "BaseStorage | None":
        """Represents the data storage engine. It is responsible for logging and managing data across 4 distinct levels, including bot data, users, chats, and conversations (Conversation Flow). If it has not been configured during bot definition or via the :meth:`set_storage` method, :obj:`None` is returned.

        See Also:
            :any:`bale.storage`
        """
        return self._storage

    def set_updater(self, updater: Type["Updater"]) -> None:
        """Use this method to set a custom updater class for receiving Bale updates via :ref:`get_updates_method`.

        Arguments:
            updater:
                The assigned class must be a subclass of :class:`~bale.Updater`. If left empty, literally nothing happens.

        Raises:
            TypeError
                If the provided class is not a valid subclass of :class:`~bale.Updater`.

        See Also:
            :doc:`topics.updates`

        .. versionadded:: 3.0
        """
        check_subclass(updater, Updater)
        self._updater = updater(self)

    def set_storage(self, storage: "BaseStorage") -> None:
        """This method configures the data storage engine for the bot.

        Arguments:
            storage: An instance of the :class:`~bale.storage.BaseStorage` class or its subclasses must be provided.

        Raises:
            TypeError
                If the provided instance is not an instance of the :class:`~bale.storage.BaseStorage` class or its subclasses.

        See Also:
            :any:`bale.storage`

        .. versionadded:: 3.0
        """
        validate_storage(storage)

        self._storage = storage

    async def _setup_hook(self) -> None:
        self._closed = False
        self.__ready_event = asyncio.Event()
        await self._http.start()

    async def __aenter__(self) -> "Bot":
        await self._setup_hook()
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback) -> None:
        await self.close()
        return None

    def listen(self, event_name: str) -> Callable[[CoroT], CoroT]:
        """A decorator that registers a function as a listener (so-called) for a specific event type.
        The function decorated by this decorator must be async.

        Arguments:
            event_name:
                The name of the event for which you want the function to be called.

        See Also:
            :any:`What is event-system? <events>`, :meth:`add_event`

        Hint:
            Default events exist within the :class:`~bale.constants.DefaultEvent`.

            .. code-block:: python

                from bale.constants import DefaultEvent

                @bot.listen(DefaultEvent.READY)
                async def ready_event_wrapper():
                    print(bot.user)
        """

        def wrapper(func: CoroT) -> CoroT:
            self.add_event(event_name, func)
            return func

        return wrapper

    def handle(self, handler: HandlerT) -> Callable[[CoroT], HandlerT]:
        """A decorator that registers the input function as a callback for an instance of an update handler.

        Arguments:
            handler:
                An instance of the handler for which you want the function registered as a callback. It must be an instance of :class:`~.handlers.UpdateHandler` or its subclasses, such as :class:`.CommandHandler`. You can even create a custom subclass of :class:`.UpdateHandler` and pass an instance of it to the parameter.

        See Also:
            :any:`What is handler? <bale.handlers>`, :meth:`~bale.Bot.add_handler`

        Warning:
            The parameters of the function provided as the handler’s callback may vary depending on the type of handler you use and what response that handler returns to its internal ``check_update`` method (:meth:`.UpdateHandler.check_update`). The response of your handler to this method will be passed directly to the function you provide as a parameter.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.handlers import MessageHandler
                from bale.context import Context

                @bot.handle(MessageHandler())
                async def message_handler(ctx: Context) -> None:
                    await ctx.reply("Cool!")

        """

        def wrapper(func: CoroT) -> HandlerT:
            self.add_handler(handler, func)
            return handler

        return wrapper

    def add_handler(self, handler: "UpdateHandler", wrapper: Callable) -> None:
        """Set a wrapper for a handler.
        Once set, each time this event is triggered by the dispatch method, the callback set for that event is called.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.handlers import MessageHandler

                ...
                async def message_handler_wrapper(message: bale.Message) -> None:
                    await message.reply("Cool!")

                bot.add_handler(MessageHandler(), message_handler_wrapper)

        Arguments:
            handler:
                a :class:`~bale.handlers.UpdateHandler` instance.
            wrapper:
                Function to set as wrapper for handler.
        """
        from .handlers import \
            UpdateHandler  # pylint: disable=import-outside-toplevel

        if not iscoroutinefunction(wrapper):
            raise TypeError(f"{wrapper.__name__} is not a coroutine function")

        if not isinstance(handler, UpdateHandler):
            raise TypeError("handler must be a UpdateHandler instance")

        handler.set_callback(wrapper)
        self._handlers.append(handler)

    def add_event(self, event_name: str, func: CoroT) -> None:
        """Use this method to add a function for handling the target event.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                ...
                async def ready_event_wrapper() -> None:
                    print(bot.user)

                bot.add_event('on_ready', ready_event_wrapper)

        Arguments:
            event_name:
                The name of the event. For default events, you can use :class:`.constants.DefaultEvent`.
            func:
                The function to be used as the event handler.

        See Also:
            :any:`What is event-system? <events>`, :meth:`listen`
        """
        if not iscoroutinefunction(func):
            raise TypeError(f"{func.__name__} is not a coroutine function")

        if not self._listeners.get(event_name):
            self._listeners[event_name] = [func]
        else:
            listeners = self._listeners[event_name]
            listeners.append(func)

    def flow(self, flow: FlowT) -> FlowT:
        """A decorator used to register a custom conversation flow class.

        See Also:
            :meth:`add_flow`

        .. versionadded:: 3.0
        """
        self.add_flow(flow)
        return flow

    def add_flow(self, flow: Type["ConversationFlow"]) -> None:
        """Use this method to register a custom conversation flow class.

        Note:
            Before starting to use a conversation flow (using the :meth:`start_conversation_flow` method), you must register its class with the bot. This is necessary so that upon re-invoking the bot, previous conversation flows that are still active can be restored.

        See Also:
            :doc:`bale.conversationflow`

        Raises:
            TypeError
                If the provided instance is not an instance of the :class:`.ConversationFlow` class or its subclasses.
            ValueError
                If the provided instance has already been registered in the class.

        .. versionadded:: 3.0
        """
        from bale.flow import ConversationFlow

        check_subclass(flow, ConversationFlow)

        if flow in self._registered_flows:
            raise ValueError(f"Flow '{flow}' is already added to the list.")

        self._registered_flows.add(flow)

    def add_middleware(self, middleware: "BaseMiddleware") -> None:
        """Use this method to add a middleware instance.

        Arguments:
            middleware:
                The middleware instance must be of type :class:`.BaseMiddleware` or its subclasses.

        Note:
            When processing new updates, middlewares are responsible for quickly inspecting the update before it is processed by conversation flows or update handlers, and they have the ability to “drop” (reject) the update so that it will not be processed by conversation flows and update handlers.

        Raises:
            TypeError
                If the provided instance is not an instance of the :class:`.BaseMiddleware` class or its subclasses.
            ValueError
                If the provided instance has already been registered in the class.

        .. versionadded:: 3.0
        """
        from bale.middleware import BaseMiddleware

        if not isinstance(middleware, BaseMiddleware):
            raise TypeError(
                f"Expected an instance of BaseMiddleware, got {type(middleware).__name__} instead."
            )

        if middleware in self._middlewares:
            raise ValueError(f"Middleware '{middleware}' is already added to the list.")

        self._middlewares.append(middleware)

    async def start_conversation_flow(
        self,
        context: "Context",
        flow: Type["ConversationFlow"],
        *args,
        timeout: SentinelOrValue[int | float] = MISSING,
    ) -> None:
        """Use this method to start a predefined conversation. This method first calls the conversation flow’s entry (:meth:`.ConversationFlow.entry`) method in order, and then invokes the initiated conversation flow within the :meth:`process_new_update` method—each time after checking the middlewares and before starting the handler processing phase.

        Raises:
            RuntimeError
                If the unique key of the conversation flow already exists among the active conversation flows.

        See Also:
            :doc:`bale.conversationflow`

        .. versionadded:: 3.0
        """
        from bale.flow import ConversationFlow

        if not isinstance(flow, type) or not issubclass(flow, ConversationFlow):
            raise TypeError(
                f"Expected a subclass of ConversationFlow, got {type(flow).__name__} instead."
            )

        if flow not in self._registered_flows:
            raise ValueError(
                f"Flow {flow.__name__!r} is not registered. "
                f"Please register it via 'bot.add_flow({flow.__name__})' before starting it."
            )

        key = flow.extract_key(context)

        def find(fl: "ConversationFlow"):
            return fl.initial_key == key

        elm = _find(find, self._flows)

        if elm is not None:
            elm = elm[1]
            raise RuntimeError(
                f"Cannot start {flow.__name__}: key {key!r} is already occupied by "
                f"an active flow ({elm}). "
                f"Stop the existing flow before starting a new one."
            )

        flow_instance = flow(initial_key=key, storage=self._storage, timeout=timeout)
        if flow_instance in self._flows:
            raise RuntimeError(
                f"Flow instance {flow_instance!s} is already active in flows."
            )

        await flow_instance.invoke(context, *args)
        self._flows.add(flow_instance)

    async def wait_for(
        self,
        context: "Context",
        handler: "UpdateHandler",
        key: "Callable[[Context], Any] | ConversationFlowTarget | None" = None,
        timeout: int | float | None = None,
        invoke_handlers: bool = False,
    ) -> "Context":
        """Use this method to create a small-scale conversation flow (in a single step). It is actually used to wait for receiving a specific update.
        This method halts code execution until an update matching the specified update handler is received.

        Arguments:
            context:
                The context used as the basis for identification (user, chat, chat member, etc.) to determine the unique key of the conversation flow. The conversation flow key is generated from this context.
            handler:
                The handler that specifies the condition for receiving the next update. It must be an instance of :class:`.handlers.UpdateHandler` or its subclasses.
            key:
                A function that takes a context and returns a key. It can also be one of the :class:`~.constants.ConversationFlowTarget` values. If not provided, it defaults to the user (:attr:`~.constants.ConversationFlowTarget.USER`).
            timeout:
                The maximum waiting duration in seconds. If no update matching the handler (linked) is received, a :exc:`TimeoutError` will be raised.
            invoke_handlers:
                Determines whether update handlers should process the update after receiving the desired update of the specified handler. Defaults to :obj:`False`.

        Returns:
            Returns the context associated with the received update—which matches the :paramref:`handler` parameter.

        Raises:
            asyncio.TimeoutError
                If the timeout parameter has been set and that timeout has expired.
            RuntimeError
                If the key generated by the key builder (:paramref:`key`) for the provided context (context) already exists.

        .. versionchanged:: 3.0
        """
        from bale.flow import ConversationFlow, step

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        if key is None:
            key = ConversationFlowTarget.USER

        class _WaitForFlow(ConversationFlow, key=key):
            async def entry(self, context: "Context"):
                return self.transition(self.capture_step, timeout=timeout)

            async def _set_current_step(self, *args, **kwargs) -> None:
                pass

            async def _get_current_step(self, *args, **kwargs):
                return self.capture_step

            async def _drop_state(self, *args, **kwargs) -> None:
                pass

            @step(handler, timeout)
            async def capture_step(self, context: "Context", *_):
                if not future.done():
                    future.set_result(context)
                return self.transition(self.END, invoke_handlers=invoke_handlers)

            async def on_timeout(self) -> None:
                if not future.done():
                    future.set_exception(asyncio.TimeoutError("wait_for timed out."))
                return None

        flow_key = _WaitForFlow.extract_key(context)

        def find(fl: "ConversationFlow"):
            return fl.initial_key == flow_key

        async with self._flows_lock:
            elm = _find(find, self._flows)
            if elm is not None:
                elm = elm[1]
                raise RuntimeError(
                    f"Cannot initiate 'wait_for': target key {flow_key!r} is currently occupied "
                    f"by an active flow ({elm}). "
                    f"A waiting operation cannot be scheduled while another flow is active for this identity."
                )

            flow_instance = _WaitForFlow(flow_key, self._storage)
            await flow_instance.invoke(context)
            self._flows.add(flow_instance)

        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            async with self._flows_lock:
                self._flows.discard(flow_instance)

    async def close(self) -> None:
        """This method closes and releases the bot’s connection to the Bale server and all resources currently in use."""
        if self.is_closed():
            raise RuntimeError("The bot is already closed.")
        if self.__updater_fetcher_task:
            await self.update_queue.put(STOP_UPDATER_MARKER)
            await self.update_queue.join()

        await asyncio.gather(*self.__tasks, return_exceptions=True)
        if not self.http_is_closed():
            await self._http.close()

        self.__updater_fetcher_task = None
        self._client_user = None
        self._closed = True

        _log.info("Closing operation was successfully completed")

    async def request(
        self,
        api_route: APIEndpoint | None = None,
        method: str | None = None,
        endpoint: str | None = None,
        handle_rate_limit: bool = True,
        **kwargs,
    ) -> BaleResponse:
        """Sends an HTTP request to the Bale web service. This method is responsible for establishing connection with the server, sending the request, as well as receiving and processing its response.

        This method is used to send HTTP requests to an API and supports
        various HTTP methods such as GET, POST, PUT, DELETE, etc. and automatically handles cases such as rate limit management, etc.

        .. code-block:: python

            await bot.request("POST", "/sendMessage")

        Arguments:
            api_route:
                A standard and predefined route of type :class:`~.constants.APIEndpoint` that specifies the method and the endpoint address. If this parameter is provided, there is no need for :paramref:`method` or :paramref:`endpoint` parameters.
            method:
                The HTTP method to be used (e.g. ``GET``, ``POST``, ``PUT`` & ``DELETE``). If the api_route parameter is not provided, it must be provided along with endpoint.
            endpoint:
                The endpoint URL of the request. If the api_route parameter is not provided, it must be provided along with method.
            handle_rate_limit:
                Specifies whether the error related to the request rate limit of the Bale bot web service should be handled automatically or not. The default value is :obj:`True`.
            kwargs:
                This parameter is directly passed to the parameters of :meth:`aiohttp.ClientSession.request` when it is called.

        Returns:
            An object containing the response received from the Bale server.

        Raises:
            TypeError
                If the method specification parameters are incomplete.
            bale.RateLimited
                If a rate limit is hit and the :paramref:`handle_rate_limit` parameter is disabled.

        .. versionadded:: 3.0
        """
        if api_route is not None:
            if not isinstance(api_route, APIEndpoint):
                raise TypeError("api_route must be a subclass of bale.APIEndpoint")
            method, endpoint = api_route.value
        elif method is None or endpoint is None:
            raise TypeError(
                "either 'api_route' or both 'method' and 'endpoint' must be provided."
            )

        if "components" in kwargs:
            message = (
                "The 'components' parameter is deprecated and will be removed in a future version. "
                "Please use 'reply_markup' instead."
            )
            components = kwargs.pop("components")
            if "reply_markup" not in kwargs:
                message += " It has been automatically converted to 'reply_markup' for now, but this will no longer be supported in the next release."
                kwargs["reply_markup"] = components

            warnings.warn(message, category=FutureWarning, stacklevel=2)

        for key in list(kwargs.keys()):
            if key.startswith("request_"):
                kwargs[key.removeprefix("request_")] = kwargs.pop(key)

        handle_rate_limit = kwargs.pop("handle_rate_limit", True)
        if form_data_payload := kwargs.pop("form_data_payload", None):
            kwargs["form_data"] = utils_request.build_form_data(form_data_payload)
        if json := kwargs.get("json"):
            kwargs["json"] = utils_request.build_payload(json)

        if maybe_form_data := kwargs.pop("maybe_form_data", None):
            json, form_data = utils_request.maybe_form_data(maybe_form_data)
            if json:
                kwargs["json"] = json
            if form_data:
                kwargs["form_data"] = form_data

        route = Route(method, endpoint, self.token)

        async def do_request():
            try:
                return await self._http.request(route, **kwargs)
            except RateLimited as exc:
                _log.debug("[%s] %s Received a 429 status code", method, route.url)
                if not handle_rate_limit:
                    raise
                retry_after = exc.retry_after or 5
                await asyncio.sleep(retry_after)
                return await do_request()

        return await do_request()

    def is_closed(self) -> bool:
        """:obj:`bool`: Bot Status"""
        return self._closed

    def http_is_closed(self) -> bool:
        """:obj:`bool`: HTTPClient Status"""
        return self._http.is_closed()

    async def run_event(self, core: CoroT, method: str, *args, **kwargs) -> None:
        try:
            await core(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if method != "on_event_error":  # dispatch loop is near!
                try:
                    self.dispatch("event_error", method, exc)
                except asyncio.CancelledError:
                    pass

    def _create_event_schedule(
        self, core: CoroT, method: str, *args, **kwargs
    ) -> asyncio.Task[None]:
        task = self.run_event(core, method, *args, **kwargs)
        return self.create_task(task, name=f"Bot:process_event:{method}")

    def dispatch(self, event_name: str, /, *args, **kwargs) -> None:
        """This method invokes all event handlers (listeners) for a given event.

        For example, if there is a need to invoke the handlers for the `on_update <events.html#on_update>`_ event, you can register your listener and then trigger it using the dispatch method:

        .. code-block:: python

            from bale import Update

            @client.listen('on_update')
            async def on_update_handler(update: Update):
                # This handler gets called when the event is dispatched
                print(update)

        .. admonition:: Triggering the Event
            :class: tip

            Wherever you need to fire this event, use:

            .. code-block:: python

                client.dispatch('on_update', update)

        See Also:
            :doc:`events`
        """
        method = "on_" + event_name
        if default_callback := getattr(self, method, None):
            if default_callback and not iscoroutinefunction(default_callback):
                _log.warning("event %s default callback is not a coroutine!", method)
            self._create_event_schedule(default_callback, method, *args, **kwargs)

        if funcs := self._listeners.get(method):
            for coro in funcs:
                if not iscoroutinefunction(coro):
                    _log.warning("event %s callback is not a coroutine!", method)
                    continue
                self._create_event_schedule(coro, method, *args, **kwargs)

    async def wait_for_ready(self) -> None:
        """This method halts code execution until the bot is fully up and ready.

        In fact, it guarantees that the next line of this code will run only when all initial setup steps, connection to the Bale web service, and retrieval of initial information (such as the bot’s user profile) have been successfully completed.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                async def send_message_after_get_ready():
                    await bot.wait_for_ready()
                    await bot.send_message(chat_id, "I'm ready!")

        .. versionadded:: 3.0
        """
        if self.__ready_event is None:
            raise RuntimeError(
                "Bot is not initialized. Ensure the bot is running "
                "before calling wait_for_ready()."
            )

        await self.__ready_event.wait()

    async def on_ready(self):
        """Called automatically after all initializations are complete and the bot account is successfully fetched via :meth:`~Bot.get_me`.

        Hint:
            By default, it logs basic identity information of the bot.
            To customize the behavior, override this method in a subclass of the Bot object.
        """
        u = self.user
        if u is None:
            raise RuntimeError(
                "cannot log in: Bot.user is None! "
                "Ensure the bot has successfully authenticated and fetched user data before accessing this."
            )

        bot_account = u and (u.mention or u.first_name)
        _log.info("Logged in as %s", bot_account)

    async def on_handler_error(
        self,
        handler: "UpdateHandler",
        update: "Update",  # noqa
        exc: Exception,
    ):
        _log.exception(
            "Exception in callback function of %s handler Ignored",
            getattr(
                handler.callback, "__qualname__", f"(callback function of {handler}"
            ),
            exc_info=exc,
        )

    async def on_event_error(self, event_name: str, exc: Exception):
        _log.exception("Exception in %s event Ignored", event_name, exc_info=exc)

    async def on_middleware_process_error(
        self, middleware: "BaseMiddleware", exc: Exception
    ) -> None:
        _log.exception("Exception in %s middleware Ignored", middleware, exc_info=exc)

    async def get_me(self, **kwargs) -> User:
        """This method authenticates the bot’s basic information and profile to verify the token’s validity.

        Returns:
             The bot’s user information and profile.

        Note:
            Every time this method is called, the information stored in the :attr:`user` property is updated and cached.
        """
        response = await self.request(APIEndpoint.GET_ME, **kwargs)
        client_user = User.from_dict(data=response.result, bot=self)
        self._client_user = client_user
        return cast(User, client_user)

    getMe = get_me
    """A alias for :meth:`get_me`.
    
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def set_webhook(self, url: str, **kwargs) -> bool:
        """This method sets an address for Bale so that new bot updates are sent via that link as a webhook.
        By configuring the webhook, whenever a new update occurs for the bot, the Bale server sends an HTTPS POST request to the address specified in the :paramref:`url`, containing the update information. If the request sent through Bale is unsuccessful (returning status codes other than 2XY), the Bale server gives up on retrying after a few attempts.

        Arguments:
            url:
                The HTTPS URL for receiving updates. To remove and disable the webhook, an empty string can also be used.

        .. code-block:: python

            await bot.set_webhook("https://example.com")

        Returns:
            Returns :obj:`True` if the operation is successful, and :obj:`False` otherwise.
        """
        payload = {"url": url}
        response = await self.request(APIEndpoint.SET_WEBHOOK, json=payload, **kwargs)
        return cast(bool, response.result)

    setWebhook = set_webhook
    """A alias for :meth:`set_webhook`.
    
    .. versionadded:: 3.0
    """

    async def delete_webhook(self, **kwargs) -> bool:
        """This method removes the webhook configuration so that manual fetching of updates (:ref:`get_updates_method`) can be used again.

        .. code-block:: python

            await bot.delete_webhook()

        Returns:
             Returns :obj:`True` if the operation is successful, and :obj:`False` otherwise.

        See Also:
            :ref:`webhooks_method`
        """
        response = await self.request(APIEndpoint.DELETE_WEBHOOK, **kwargs)
        return cast(bool, response.result)

    deleteWebhook = delete_webhook
    """A alias for :meth:`delete_webhook`.
    
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This method sends a new text message to the target chat.

        .. code-block:: python

            await bot.send_message(6429983203, "hi, python-bale-bot!", ...)

        Returns:
             The Message.

        Arguments:
            chat_id:
                |chat_id|
            text:
                The text of the message to be sent. It must be at most ``4096`` characters long.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(APIEndpoint.SEND_MESSAGE, json=payload, **kwargs)
        result = Message.from_dict(data=response.result, bot=self)

        return cast(Message, result)

    sendMessage = send_message
    """A alias for :meth:`send_message`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def forward_message(
        self,
        chat_id: str | int,
        from_chat_id: str | int,
        message_id: str | int,
        **kwargs,
    ) -> "Message":
        """This method is used to forward a message to the target chat.

        .. code-block:: python

            await bot.forward_message(6429983203, 6429983203, 123)

        Arguments:
            chat_id:
                The destination chat for forwarding the message.
            from_chat_id:
                The unique identifier of the chat where the original message is located (or the channel username, which can be in the format @channelusername).
            message_id:
                The unique identifier of the target message specified within the :paramref:`from_chat_id` chat.

        Returns:
             The newly forwarded message.
        """
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
        }

        response = await self.request(
            APIEndpoint.FORWARD_MESSAGE, json=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    forwardMessage = forward_message
    """A alias for :meth:`forward_message`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_document(
        self,
        chat_id: str | int,
        document: "Document | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send a file or document to the target chat.

        .. code-block:: python

            await bot.send_document(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            document:
                Document file to send. |file|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "document": parse_file_input(document, Document, file_name),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_DOCUMENT, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendDocument = send_document
    """A alias for :meth:`send_document`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_photo(
        self,
        chat_id: str | int,
        photo: PhotoSize | FileInput,
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send an image to the target chat.

        .. code-block:: python

            await bot.send_photo(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            photo:
                Photo file to send. |file|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "photo": parse_file_input(photo, PhotoSize, file_name),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_PHOTO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendPhoto = send_photo
    """A alias for :meth:`send_photo`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_audio(
        self,
        chat_id: str | int,
        audio: Audio | FileInput,
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send an audio file playable in the Bale player to the target chat.

        .. code-block:: python

            await bot.send_audio(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            audio:
                Audio file to send. |file|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "audio": parse_file_input(audio, Audio, file_name),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_AUDIO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendAudio = send_audio
    """A alias for :meth:`send_audio`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_voice(
        self,
        chat_id: str | int,
        voice: Voice | FileInput,
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send a recorded voice message (commonly known as a voice note) to the target chat.

        .. code-block:: python

            await bot.send_voice(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            voice:
                Voice file to send. |file|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.

        .. versionadded:: 3.0
        """
        payload = {
            "chat_id": chat_id,
            "voice": parse_file_input(voice, Voice, file_name),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_VOICE, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendVoice = send_voice
    """A alias for :meth:`send_voice`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_video(
        self,
        chat_id: str | int,
        video: Video | FileInput,
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send a video to the target chat.

        .. code-block:: python

            await bot.send_video(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            video:
                Video file to send. |file|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "video": parse_file_input(video, Video, file_name),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_VIDEO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendVideo = send_video
    """A alias for :meth:`send_video`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_animation(
        self,
        chat_id: str | int,
        animation: Animation | FileInput,
        *,
        duration: SentinelOrValue[int] = MISSING,
        width: SentinelOrValue[int] = MISSING,
        height: SentinelOrValue[int] = MISSING,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        file_name: str | None = None,
        **kwargs,
    ) -> "Message":
        """This method is used to send a GIF to the target chat.

        .. code-block:: python

            await bot.send_animation(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            animation:
                Animation file to send. |file|
            duration:
                The duration of the animation in seconds.
            width:
                The width of the animation in pixels.
            height:
                The height of the animation in pixels.
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|
            file_name:
                |file_name|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "animation": parse_file_input(animation, Animation, file_name),
            "duration": duration,
            "width": width,
            "height": height,
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_ANIMATION, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendAnimation = send_animation
    """A alias for :meth:`send_animation`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_media_group(
        self,
        chat_id: str | int,
        media: list[MediaInput],
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> tuple["Message"]:
        """This method sends a group of media (photos, videos, documents, or audio) as a single album.

        .. code-block:: python

            FIRST_FILE_ID = "799592101:3289413075816029955:0:803c486c6138301bfeaa26e9ea77ca67a726644b33c0e3724469ee96a4ee17f8de5f2031f58dfcb943e8491eb5bdf3cd97331796b1e0167d"
            SECOND_FILE_ID = "799592101:-1553246196730945791:0:b0692a640412bd72d72b97e6079604280c6133a8cfb41780670d4f669243d25c97b8aae6c578d5df8211e6c76420e4b7"
            THIRD_FILE_ID = "799592101:5494303441778450178:0:599796d54528a89f3c7c9416dc14f67aa0cd08207d7beefced155c90cbd90c4d3d4a0775b8f05868388bbc9c2b10ed921a228f748c9eca11"

            await bot.send_media_group(6429983203, [
                InputMediaPhoto(FIRST_FILE_ID, caption="first caption"),
                InputMediaPhoto(SECOND_FILE_ID),
                InputMediaPhoto(THIRD_FILE_ID, caption="second caption"),
            ], ...)

        Important:
            You can combine photos and videos in a single group, but mixing other media types (such as audio and documents) in the same group is not supported.

        Note:
            Messages sent as a group share the same :attr:`.Message.media_group_id`.

        Arguments:
            chat_id:
                |chat_id|
            media:
                Files to send.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Messages.

        See Also:
            :ref:`media_group`
        """
        payload = {
            "chat_id": chat_id,
            "media": media,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }
        json, form_data_payload = utils_request.build_media_group(payload)
        if json:
            kwargs["json"] = json
        if form_data_payload:
            kwargs["form_data_payload"] = form_data_payload

        response = await self.request(APIEndpoint.SEND_MEDIA_GROUP, **kwargs)
        messages = Message.from_list(payloads_list=response.result, bot=self)

        return cast(tuple[Message], messages)

    sendMediaGroup = send_media_group
    """A alias for :meth:`send_media_group`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_location(
        self,
        chat_id: str | int,
        location: "Location",
        *,
        reply_markup: SentinelOrValue["ReplyMarkupT"] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This method is used to send a location on the map to the target chat.

        .. code-block:: python

            await bot.send_location(6429983203, bale.Location(35.71470468031143, 51.8568519168293))

        Arguments:
            chat_id:
                |chat_id|
            location:
                The Location object containing coordinates.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "horizontal_accuracy": location.horizontal_accuracy,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(APIEndpoint.SEND_LOCATION, json=payload, **kwargs)
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendLocation = send_location
    """A alias for :meth:`send_location`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_contact(
        self,
        chat_id: str | int,
        contact: "Contact",
        *,
        reply_markup: SentinelOrValue[ReplyMarkupT] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This method is used to send a contact.

        .. code-block:: python

            await bot.send_contact(6429983203, bale.Contact('09****', 'first name', 'last name'))

        Arguments:
            chat_id:
                |chat_id|
            contact:
                The Contact object.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "phone_number": contact.phone_number,
            "first_name": contact.first_name,
            "last_name": contact.last_name or MISSING,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(APIEndpoint.SEND_CONTACT, json=payload, **kwargs)
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendContact = send_contact
    """A alias for :meth:`send_contact`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_invoice(
        self,
        chat_id: str | int,
        title: str,
        description: str,
        provider_token: str,
        prices: list["LabeledPrice"],
        *,
        invoice_payload: SentinelOrValue[str] = MISSING,
        photo_url: SentinelOrValue[str] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> Message:
        """This method is used to send a payment request (invoice).

        .. code-block:: python

            await bot.send_invoice(
                6429983203, "invoice title", "invoice description", "6037************", [bale.LabeledPrice("label", 2000)],
                invoice_payload = "unique invoice payload", ...
            )

        .. admonition:: Examples

            :any:`Payment Bot <examples.invoice>`

        Arguments:

            chat_id:
                |chat_id|
            title:
                The request title. It can be a maximum of ``32`` characters.
            description:
                The request description. It can be a maximum of ``255`` characters.
            provider_token:
                Payment methods:
                    1. Card number
                        .. deprecated:: 3.0
                    2. Terminal ID and Merchant ID (``terminal_id:acqrID``)
                        .. deprecated:: 3.0
                    3. Unique Bale wallet identifier
            prices:
                A list of invoice items.
            invoice_payload:
                Payload defined by the bot for this request. Use it to distinguish between payment requests. The maximum allowed length for this parameter is ``128`` bytes. This data will be visible in the :class:`.PreCheckoutQuery` and :class:`.SuccessfulPayment` objects as the transaction progresses and is finalized.
            photo_url:
                The URL of the invoice image, which must be in HTTPS format.
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.

        See Also:
            :doc:`bale.payments`
        """
        payload = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "provider_token": provider_token,
            "prices": [price.to_dict() for price in prices],
            "payload": invoice_payload,
            "photo_url": photo_url,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(APIEndpoint.SEND_INVOICE, json=payload, **kwargs)
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendInvoice = send_invoice
    """A alias for :meth:`send_invoice`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_sticker(
        self,
        chat_id: str | int,
        sticker: Sticker | FileInput,
        *,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This method is used to send a sticker.

        .. code-block:: python

            await bot.send_sticker(6429983203, "FILE ID", ...)

        Arguments:
            chat_id:
                |chat_id|
            sticker:
                To send a sticker that already exists on Bale servers, pass its unique ``file_id`` as a string. Alternatively, you can provide an HTTP URL for Bale to download and upload, or pass a local file path (:obj:`str` or :obj:`Path`) for the library to upload.
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        if isinstance(sticker, Sticker):
            sticker = sticker.file_id

        payload = {
            "chat_id": chat_id,
            "sticker": parse_file_input(sticker),
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_STICKER, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result, bot=self)
        return cast(Message, result)

    sendSticker = send_sticker
    """A alias for :meth:`send_sticker`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def send_chat_action(self, chat_id: str | int, action: str, **kwargs) -> bool:
        """This service is used to send chat action.

        .. code-block:: python

            from bale.constants import ChatAction

            await bot.send_chat_action(6429983203, ChatAction.TYPING)

        Arguments:
            chat_id:
                |chat_id|
            action:
                The action you want to display to the user in the specified chat. It can be any of the properties from the `.constants.ChatAction` class.

        Returns:
             On success, :obj:`True` is returned.

        :ref:`chat_actions_context_manager`

        .. versionadded:: 3.0
        """
        payload = {"chat_id": str(chat_id), "action": action}

        response = await self.request(
            APIEndpoint.SEND_CHAT_ACTION, json=payload, **kwargs
        )
        return cast(bool, response.result)

    sendChatAction = send_chat_action
    """A alias for :meth:`send_chat_action`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def edit_message_text(
        self,
        chat_id: str | int,
        message_id: str | int,
        text: str,
        *,
        reply_markup: SentinelOrValue["InlineKeyboardMarkup"] = MISSING,
        **kwargs,
    ) -> "Message":
        """Use this method to edit a text message.

        .. code-block:: python

            await bot.edit_message_text(6429983203, 6429983203, "the message edited!", reply_markup=None)

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                Unique identifier of the message to edit.
            text:
                New text for the message, up to ``4096`` characters.
            reply_markup:
                Additional interface settings; must represent an inline keyboard markup. To update only this parameter, use the :meth:`edit_message_reply_markup` method instead.

        Returns:
            The edited message.
        """
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": reply_markup,
        }

        response = await self.request(
            APIEndpoint.EDIT_MESSAGE_TEXT, json=payload, **kwargs
        )
        result = Message.from_dict(response.result, self)
        return cast(Message, result)

    editMessageText = edit_message_text
    """A alias for :meth:`edit_message_text`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def edit_message_caption(
        self,
        chat_id: str | int,
        message_id: str | int,
        caption: str,
        *,
        reply_markup: SentinelOrValue["InlineKeyboardMarkup"] = MISSING,
        **kwargs,
    ) -> "Message":
        """Use this method to edit the caption of a media message.

        Tip:
            When editing the caption of a media group (album) message, keep in mind that each item in the album is treated as a separate message.

        .. code-block:: python

            await bot.edit_message_caption(6429983203, 6429983203, "the message edited!", reply_markup=None)

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                 Unique identifier of the message to edit.
            caption:
                The new caption of the message. It can be at most ``4096`` characters.
            reply_markup:
                Additional interface settings; must represent an inline keyboard markup. To update only this parameter, use the :meth:`edit_message_reply_markup` method instead.

        Returns:
            The edited message.

        .. versionadded:: 3.0
        """
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": caption,
            "reply_markup": reply_markup,
        }

        response = await self.request(
            APIEndpoint.EDIT_MESSAGE_CAPTION, json=payload, **kwargs
        )
        result = Message.from_dict(response.result, self)
        return cast(Message, result)

    editMessageCaption = edit_message_caption
    """A alias for :meth:`edit_message_caption`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def edit_message_reply_markup(
        self,
        chat_id: str | int,
        message_id: str | int,
        reply_markup: SentinelOrValue["InlineKeyboardMarkup"],
        **kwargs,
    ) -> "Message":
        """Use this method to edit the UI settings of any message. In other words, this method can be used to edit the inline keyboards of both text and media messages.

        .. code-block:: python

            await bot.edit_message_reply_markup(6429983203, 123456, reply_markup=None)

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                Unique identifier of the message to edit.
            reply_markup:
                Additional interface settings; must represent an inline keyboard markup.

        Returns:
            The edited message.

        .. versionadded:: 3.0
        """
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": reply_markup,
        }

        response = await self.request(
            APIEndpoint.EDIT_MESSAGE_REPLY_MARKUP, json=payload, **kwargs
        )
        result = Message.from_dict(response.result, self)
        return cast(Message, result)

    editMessageReplyMarkup = edit_message_reply_markup
    """A alias for :meth:`edit_message_reply_markup`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def copy_message(
        self,
        chat_id: str | int,
        from_chat_id: str | int,
        message_id: str | int,
        *,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """Use this method to copy and send a previously sent message. This works like :meth:`forward_message`, but without displaying the original chat name or author.

        .. code-block:: python

            await bot.copy_message(6429983203, 6429983203, 123)

        Arguments:
            chat_id:
                |chat_id|
            from_chat_id:
                The unique identifier of the chat where the original message is located (or the channel username, which can be in the format @channelusername).
            message_id:
                The unique identifier of the target message specified within the :paramref:`from_chat_id` chat.
            reply_to_message_id:
                |reply_to_message_id|
        """
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(APIEndpoint.COPY_MESSAGE, json=payload, **kwargs)
        result = Message.from_dict(response.result, self)
        return cast(Message, result)

    copyMessage = copy_message
    """A alias for :meth:`copy_message`.
    
    .. versionadded:: 3.0
    """

    @overload
    async def delete_message(
        self, chat_id: str | int, message_id: str | int, *, delay: int | float, **kwargs
    ) -> asyncio.Task[bool]: ...

    @overload
    async def delete_message(
        self, chat_id: str | int, message_id: str | int, *, delay: None = None, **kwargs
    ) -> bool: ...

    @arguments_shield
    async def delete_message(
        self,
        chat_id: str | int,
        message_id: str | int,
        *,
        delay: int | float | None = None,
        **kwargs,
    ) -> bool | asyncio.Task[bool]:
        """Use this method to delete a previously sent message.

        .. code-block:: python

            await bot.delete_message(6429983203, 6429983203)

        .. warning::
            In channels or groups, only when the admin can delete other people's messages.
            Otherwise, It's no limit to delete his own message.

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                Unique identifier of the message to delete.
            delay:
                If used, the message will be deleted after that number of seconds delay.

        Returns:
            If the :paramref:`delay` parameter is used, a message deletion task object is returned after the specified duration; otherwise, the result of the operation is indicated by a boolean value.
        """
        if delay is not None and delay <= 0:
            raise ValueError("delay param must be positive")

        payload = {"chat_id": chat_id, "message_id": message_id}

        async def worker() -> bool:
            """This function deletes a specific message after a certain number of seconds."""
            if delay is not None:
                await asyncio.sleep(delay)

            result = await self.request(
                APIEndpoint.DELETE_MESSAGE, json=payload, **kwargs
            )
            return cast(bool, result.ok)

        if delay:
            return self.create_task(
                worker(), name=f"Bot:delete_message_task:{chat_id}:{message_id}"
            )
        return await worker()

    deleteMessage = delete_message
    """A alias for :meth:`delete_message`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_chat(self, chat_id: str | int, **kwargs) -> "ChatFullInfo | None":
        """Use this method to get information about any chat, regardless of its type.

        .. code-block:: python

            await bot.get_chat(6429983203)

            await bot.get_chat("6429983203")

        Arguments:
            chat_id:
                 |chat_id|

        Returns:
             The chat or :obj:`None` if not found.
        """

        payload = {"chat_id": str(chat_id)}

        try:
            response = await self.request(APIEndpoint.GET_CHAT, json=payload, **kwargs)
        except NotFound:
            return None

        chat = ChatFullInfo.from_dict(response.result, bot=self)
        return cast(ChatFullInfo, chat)

    getChat = get_chat
    """A alias for :meth:`get_chat`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_user(self, user_id: str | int, **kwargs) -> "User | None":
        """Use this method to get information about a private chat, returning a :class:`.User` object.

        .. code-block:: python

            await bot.get_user(6429983203)
            # or
            await bot.get_user("6429983203")

        Arguments:
            user_id:
                 The unique identifier of the target user account.

        Returns:
             The user or :obj:`None` if not found.
        """
        chat = await self.get_chat(user_id, **kwargs)

        if chat and chat.is_private:
            result = User.from_dict(cast("UserPayload", chat.to_dict()), self)
            return cast(User, result)

        return None

    @arguments_shield
    async def get_chat_member(
        self, chat_id: str | int, user_id: str | int, **kwargs
    ) -> "ChatMember | None":
        """Use this method to retrieve information about a chat member. Note that the chat must be a group or a channel, and the bot must be an administrator.

        .. code-block:: python

            await bot.get_chat_member(6429983203, 6429983203)

        Arguments:
            chat_id:
                |chat_id|
            user_id:
                |user_id|

        Returns:
             The chat member of :obj:`None` if not found.
        """
        payload = {"chat_id": chat_id, "user_id": user_id}

        try:
            response = await self.request(
                APIEndpoint.GET_CHAT_MEMBER, json=payload, **kwargs
            )
        except NotFound:
            return None

        chat_member = ChatMember.from_dict(response.result, self)
        return cast(ChatMember, chat_member)

    getChatMember = get_chat_member
    """A alias for :meth:`get_chat_member`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def promote_chat_member(
        self,
        chat_id: str | int,
        user_id: str | int,
        can_send_messages: SentinelOrValue[bool] = MISSING,
        can_send_media_messages: SentinelOrValue[bool] = MISSING,
        can_send_audios: SentinelOrValue[bool] = MISSING,
        can_send_documents: SentinelOrValue[bool] = MISSING,
        can_send_photos: SentinelOrValue[bool] = MISSING,
        can_send_videos: SentinelOrValue[bool] = MISSING,
        can_send_video_notes: SentinelOrValue[bool] = MISSING,
        can_send_voice_notes: SentinelOrValue[bool] = MISSING,
        can_send_polls: SentinelOrValue[bool] = MISSING,
        can_send_other_messages: SentinelOrValue[bool] = MISSING,
        can_add_web_page_previews: SentinelOrValue[bool] = MISSING,
        can_change_info: SentinelOrValue[bool] = MISSING,
        can_invite_users: SentinelOrValue[bool] = MISSING,
        can_pin_messages: SentinelOrValue[bool] = MISSING,
        can_manage_topics: SentinelOrValue[bool] = MISSING,
        can_post_messages: SentinelOrValue[bool] = MISSING,
        can_edit_messages: SentinelOrValue[bool] = MISSING,
        can_delete_messages: SentinelOrValue[bool] = MISSING,
        can_manage_video_chats: SentinelOrValue[bool] = MISSING,
        can_restrict_members: SentinelOrValue[bool] = MISSING,
        **kwargs,
    ):
        """an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass :obj:`False` for all boolean parameters to demote a user.

        .. code-block:: python

            await bot.promote_chat_member(6429983203, 6429983203, can_change_info = True)

        Arguments:
            chat_id:
                |chat_id|
            user_id:
                |user_id|
            can_send_messages:
                :obj:`True`, if the user is allowed to send text messages, contacts, locations and venues
            can_send_media_messages:
                :obj:`True`, if the user is allowed to send media messages
            can_send_audios:
                :obj:`True`, if the user is allowed to send audio files
            can_send_documents:
                :obj:`True`, if the user is allowed to send documents
            can_send_photos:
                :obj:`True`, if the user is allowed to send photos
            can_send_videos:
                :obj:`True`, if the user is allowed to send videos
            can_send_video_notes:
                :obj:`True`, if the user is allowed to send video notes
            can_send_voice_notes:
                :obj:`True`, if the user is allowed to send voice notes
            can_send_polls:
                :obj:`True`, if the user is allowed to send polls
            can_send_other_messages:
                :obj:`True`, if the user is allowed to send animations, games, stickers and use inline bots
            can_add_web_page_previews:
                :obj:`True`, if the user is allowed to add web page previews to their messages
            can_change_info:
                :obj:`True`, if the user is allowed to change chat title, photo and other settings
            can_invite_users:
                :obj:`True`, if the user is allowed to invite new users to the chat
            can_pin_messages:
                :obj:`True`, if the user is allowed to pin messages
            can_manage_topics:
                :obj:`True`, if the user is allowed to create, rename, close, and reopen forum topics
            can_post_messages:
                :obj:`True`, if the administrator is allowed to post messages in the channel
            can_edit_messages:
                :obj:`True`, if the administrator is allowed to edit messages in the channel
            can_delete_messages:
                :obj:`True`, if the user is allowed to delete messages
            can_manage_video_chats:
                :obj:`True`, if the administrator is allowed to manage video chats
            can_restrict_members:
                :obj:`True`, if the administrator is allowed to restrict, ban or unban chat members


        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 2.5.0
        """
        response = await self.request(
            APIEndpoint.PROMOTE_CHAT_MEMBER,
            json={
                "chat_id": chat_id,
                "user_id": user_id,
                "can_send_messages": can_send_messages,
                "can_send_media_messages": can_send_media_messages,
                "can_send_audios": can_send_audios,
                "can_send_documents": can_send_documents,
                "can_send_photos": can_send_photos,
                "can_send_videos": can_send_videos,
                "can_send_video_notes": can_send_video_notes,
                "can_send_voice_notes": can_send_voice_notes,
                "can_send_polls": can_send_polls,
                "can_send_other_messages": can_send_other_messages,
                "can_add_web_page_previews": can_add_web_page_previews,
                "can_change_info": can_change_info,
                "can_invite_users": can_invite_users,
                "can_pin_messages": can_pin_messages,
                "can_manage_topics": can_manage_topics,
                "can_post_messages": can_post_messages,
                "can_edit_messages": can_edit_messages,
                "can_delete_messages": can_delete_messages,
                "can_manage_video_chats": can_manage_video_chats,
                "can_restrict_members": can_restrict_members,
            },
            **kwargs,
        )
        return cast(bool, response.result)

    promoteChatMember = promote_chat_member
    """A alias for :meth:`promote_chat_member`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def ban_chat_member(
        self, chat_id: str | int, user_id: str | int, **kwargs
    ) -> bool:
        """Use this method to ban a user from a channel or group chat. After this occurs, the user cannot rejoin the group via an invitation link unless they have been unbanned beforehand. To use this method, the bot must be an administrator in the chat and have the ``can_restrict_members`` permission.

        .. code-block:: python

            await bot.ban_chat_member(6429983203, 6429983203)

        Arguments:
            chat_id:
                |chat_id|
            user_id:
                |user_id|

        Returns:
             On success, :obj:`True` is returned.
        """
        payload = {"chat_id": chat_id, "user_id": user_id}

        response = await self.request(
            APIEndpoint.BAN_CHAT_MEMBER, json=payload, **kwargs
        )
        return cast(bool, response.result)

    banChatMember = ban_chat_member
    """A alias for :meth:`ban_chat_member`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def unban_chat_member(
        self,
        chat_id: str | int,
        user_id: str | int,
        *,
        only_if_banned: SentinelOrValue[bool] = MISSING,
        **kwargs,
    ) -> bool:
        """Use this method to unban a user from a chat.
        Note that the user is not automatically added back to the chat, but they will be able to rejoin. If the target user is present in the chat, they will be removed from the chat. To disable this behavior, set the :paramref:`only_if_banned` parameter to :obj:`True`.

        .. code-block:: python

            await bot.unban_chat_member(6429983203, 6429983203)

        Arguments:
            chat_id:
                |chat_id|
            user_id:
                |user_id|
            only_if_banned:
                 Pass :obj:`True` if the user should be unbanned only if they are currently banned from the chat.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 2.5.0
        """
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned,
        }

        response = await self.request(
            APIEndpoint.UNBAN_CHAT_MEMBER, json=payload, **kwargs
        )
        return cast(bool, response.result)

    unbanChatMember = unban_chat_member
    """A alias for :meth:`unban_chat_member`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def set_chat_photo(
        self, chat_id: str | int, photo: PhotoSize | FileInput, **kwargs
    ) -> bool:
        """Use this method to set a new profile photo for the chat.

        .. code-block:: python

            await bot.set_chat_photo(6429983203, "FILE_ID")

        Arguments:
            chat_id:
                |chat_id|
            photo:
                New chat photo. Pass the file's unique ID to this parameter to send a file that is already available on Bale servers. You can also provide the HTTP URL of the photo file as a string for Bale to upload. Alternatively, pass the file's local path as a string or a :class:`.Path` object to have the library upload it to Bale servers. This parameter can also accept an instance of a :class:`.PhotoSize` object.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 2.5.0
        """
        payload = {"chat_id": chat_id, "photo": parse_file_input(photo, PhotoSize)}

        response = await self.request(
            APIEndpoint.SET_CHAT_PHOTO, maybe_form_data=payload, **kwargs
        )
        return cast(bool, response.result)

    setChatPhoto = set_chat_photo
    """A alias for :meth:`set_chat_photo`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def delete_chat_photo(self, chat_id: str | int, **kwargs) -> bool:
        """Use this method to delete a chat photo.

        .. code-block:: python

            await bot.delete_chat_photo(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.DELETE_CHAT_PHOTO, maybe_form_data=payload, **kwargs
        )
        return cast(bool, response.result)

    deleteChatPhoto = delete_chat_photo
    """A alias for :meth:`delete_chat_photo`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def pin_chat_message(
        self, chat_id: str | int, message_id: int, **kwargs
    ) -> bool:
        """Use this method to pin a message in a chat. If the chat is a private chat, there are no restrictions for this action. Otherwise, the bot must be an administrator in the chat, and it must have the ``can_edit_messages`` permission in channels or the ``can_pin_messages`` permission in groups.

        Note:
            Currently, Bale clients allow additional permissions to be granted to administrators and users. For example, it is possible to set the “pin messages” permission for an administrator in a channel, whereas in Telegram and the Bale Bot API, such a permission is not explicitly available for channels. Consequently, the exact permission status may vary, and the descriptions for this method regarding permissions might not fully reflect the actual behavior.

        .. code-block:: python

            await bot.pin_chat_message(6429983203, 7408)

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                Identifier of a message to pin.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id, "message_id": message_id}

        response = await self.request(
            APIEndpoint.PIN_CHAT_MESSAGE, json=payload, **kwargs
        )
        return cast(bool, response.result)

    pinChatMessage = pin_chat_message
    """A alias for :meth:`pin_chat_message`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def unpin_chat_message(
        self, chat_id: str | int, message_id: int, **kwargs
    ) -> bool:
        """Use this method to remove a message from the list of pinned messages in a chat. If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have the ``can_pin_messages`` admin right in a group or ``can_edit_messages`` admin right in a channel.

        .. code-block:: python

            await bot.unpin_chat_message(6429983203, 7408)

        Arguments:
            chat_id:
                |chat_id|
            message_id:
                Identifier of a message to unpin.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id, "message_id": message_id}

        response = await self.request(
            APIEndpoint.UNPIN_CHAT_MESSAGE, json=payload, **kwargs
        )
        return cast(bool, response.result)

    unpinChatMessage = unpin_chat_message
    """A alias for :meth:`unpin_chat_message`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def unpin_all_chat_messages(self, chat_id: str | int, **kwargs) -> bool:
        """Use this method to clear the list of pinned messages in a chat. If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have the ``can_pin_messages`` admin right in a supergroup or ``can_edit_messages`` admin right in a channel.

        .. code-block:: python

            await bot.unpin_all_chat_messages(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.UNPIN_ALL_CHAT_MESSAGES, json=payload, **kwargs
        )
        return cast(bool, response.result)

    unpinAllChatMessages = unpin_all_chat_messages
    """A alias for :meth:`unpin_all_chat_messages`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def set_chat_title(self, chat_id: str | int, title: str, **kwargs) -> bool:
        """Use this method to change the title of a chat. Obviously, it has no effect in private chats. To perform this action, the bot must be an administrator and have the necessary permissions.

        .. code-block:: python

            await bot.set_chat_title(6429983203, 'new title')

        Arguments:
            chat_id:
                |chat_id|
            title:
                The new chat title. It can be a maximum of ``128`` characters.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id, "title": title}

        response = await self.request(
            APIEndpoint.SET_CHAT_TITLE, json=payload, **kwargs
        )
        return cast(bool, response.result)

    setChatTitle = set_chat_title
    """A alias for :meth:`set_chat_title`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def set_chat_description(
        self, chat_id: str | int, description: str, **kwargs
    ) -> bool:
        """Use this method to change the description of a chat. Obviously, it has no effect in private chats. To perform this action, the bot must be an administrator and have the necessary permissions.

        .. code-block:: python

            await bot.set_chat_description(6429983203, 'new description')

        Arguments:
            chat_id:
                |chat_id|
            description:
                The new chat description. It must be a maximum of ``255`` characters.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id, "description": description}

        response = await self.request(
            APIEndpoint.SET_CHAT_DESCRIPTION, json=payload, **kwargs
        )
        return cast(bool, response.result)

    setChatDescription = set_chat_description
    """A alias for :meth:`set_chat_description`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: SentinelOrValue[str] = MISSING,
        show_alert: SentinelOrValue[bool] = MISSING,
        **kwargs,
    ) -> bool:
        """Use this method to send an answer to a callback query resulting from clicking an inline button. If the :paramref:`text` parameter is provided and non-empty, the response will be displayed as a notification at the top of the chat screen. If the :paramref:`show_alert` parameter is specified and set to :obj:`True`, the response will be shown as an alert message. Furthermore, if the :paramref:`text` parameter is empty, it merely removes the loading state from the clicked button.
        Note that you have 10 seconds from the time the button is clicked to respond to it. If this 10-second duration is exceeded, the pressed button exits the waiting state, and sending a request will result in an error.

        .. figure:: /_static/images/answer-callback-query.jpg
            :alt: How callback query responses are displayed on the user’s client in two modes: notification and alert.
            :align: center
            :class: with-shadow
            :width: 480px

            **Figure** - How callback query responses are displayed on the user’s client in two modes: notification and alert. (Image source: The bot news channel, `@botNews <https://ble.ir/botNews>`_)

        .. code-block:: python

            await bot.answer_callback_query('CALLBACK_QUERY_ID')
            await bot.answer_callback_query('CALLBACK_QUERY_ID', 'I heard you clicking the button.')
            await bot.answer_callback_query('CALLBACK_QUERY_ID', 'I heard you clicking the button.', True)

        Arguments:
            callback_query_id:
                Unique identifier for the callback query to be answered.
            text:
                Text of the notification or alert to be shown to the client of the user who clicked the button. It can be a maximum of ``200`` characters.
            show_alert:
                If set to :obj:`True`, the message will be displayed as an alert; otherwise, it will be displayed as a notification at the top of the chat. If specified, the :paramref:`text` parameter must also be provided along with it.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
        }

        response = await self.request(
            APIEndpoint.ANSWER_CALLBACK_QUERY, json=payload, **kwargs
        )
        return cast(bool, response.result)

    answerCallbackQuery = answer_callback_query
    """A alias for :meth:`answer_callback_query`.
    
    .. versionadded:: 3.0
    """

    @overload
    async def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: Literal[True], **kwargs
    ) -> bool: ...

    @overload
    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: Literal[False],
        error_message: str,
        **kwargs,
    ) -> bool: ...

    @arguments_shield
    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: SentinelOrValue[str] = MISSING,
        **kwargs,
    ) -> bool:
        """Use this method to finalize a wallet transaction.

        .. code-block:: python

            await bot.answer_pre_checkout_query('QUERY_ID', True)

        Arguments:
            pre_checkout_query_id:
                Unique identifier for the query to be answered.
            ok:
                Indicates whether the bot has fulfilled the necessary conditions to finalize the transaction. If set to :obj:`False`, the :paramref:`error_message` parameter becomes mandatory.
            error_message:
                Indicates the reason for the bot's failure to approve the transaction. As long as the :paramref:`ok` parameter is set to :obj:`True`, providing this value has no effect.

        Returns:
             On success, :obj:`True` is returned.

        .. versionadded:: 3.0
        """
        if not ok and error_message is MISSING:
            raise TypeError("error_message is required when ok is False")

        payload = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
            "error_message": error_message if not ok else MISSING,
        }

        response = await self.request(
            APIEndpoint.ANSWER_PRE_CHECKOUT_QUERY, json=payload, **kwargs
        )
        return cast(bool, response.result)

    answerPreCheckoutQuery = answer_pre_checkout_query
    """A alias for :meth:`answer_pre_checkout_query`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def ask_review(
        self, user_id: int, *, delay_seconds: int | None, **kwargs
    ) -> bool:
        """Use this method to request the user’s client to submit or edit a review about the bot. A dedicated form is displayed in the user’s client, containing separate sections for submitting a review and rating, as shown in the image.

        .. figure:: /_static/images/ask-review.jpg
            :alt: How the survey is displayed in a user's client within the chat page with that bot.
            :align: center
            :class: with-shadow
            :width: 480px

            **Figure** - How the survey is displayed in a user's client within the chat page with that bot. (Image source: The bot news channel, `@botNews <https://ble.ir/botNews>`_)


        Keep in mind that sending this request does not guarantee it will be displayed immediately. The Bale server takes into account factors such as the user’s presence in the bot’s mini-app or chat page, as well as time restrictions for showing the form, and decides whether to display it. Therefore, there is no need to manually store timestamps of when this method is used to prevent the form from appearing multiple times to the user, as the Bale server manages this.
        Furthermore, the survey results will be viewable in the parent bot.

        .. code-block:: python

            await bot.ask_review(user_id=123456789, delay_seconds=5)

        Arguments:
            user_id:
                Unique identifier of the target user.
            delay_seconds:
                The delay in displaying the form to the user after the request reaches the server. If left empty, it defaults to ``0``.
                Bale’s examples for using this parameter:

                - For relatively short messages, set the value to around 3 seconds.
                - For longer messages, set this value to around 5 seconds.
                - If the user participates in the survey voluntarily (for example, by clicking on a specific button), set the value to 0 to display it immediately.

        Returns:
            :obj:`bool`: :obj:`True` on success.

        Note:
            ⚠️ This method is not part of the standard Telegram bot APIs. It is specific to Bale.

        .. versionadded:: 3.0
        """
        if delay_seconds is None:
            delay_seconds = 0

        payload = {"user_id": user_id, "delay_seconds": delay_seconds}

        response = await self.request(APIEndpoint.ASK_REVIEW, json=payload, **kwargs)
        return cast(bool, response.result)

    askReview = ask_review
    """A alias for :meth:`ask_review`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_chat_members_count(self, chat_id: str | int, **kwargs) -> int:
        """Use this method to get the number of members in a chat. It is only supported in collective chats.

        .. code-block:: python

            await bot.get_chat_members_count(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             chat members count.
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.GET_CHAT_MEMBERS_COUNT, json=payload, **kwargs
        )
        return cast(int, response.result)

    getChatMembersCount = get_chat_members_count
    """A alias for :meth:`get_chat_members_count`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_chat_members(
        self, chat_id: str | int, **kwargs
    ) -> tuple["ChatMember"]:
        """Use this method to get the members of a chat. It is only supported in collective chats.

        .. deprecated:: 3.0
            This method is currently not supported by Bale.

        .. code-block:: python

            await bot.get_chat_members(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             list of chat members.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.GET_CHAT_MEMBERS, json=payload, **kwargs
        )
        members = ChatMember.from_list(response.result, self)
        return cast(tuple[ChatMember], members)

    getChatMembers = get_chat_members
    """A alias for :meth:`get_chat_members`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_chat_administrators(
        self, chat_id: str | int, **kwargs
    ) -> list["ChatMember"]:
        """Use this method to get a list of administrators in a chat. It is only supported in collective chats.

        .. code-block:: python

            await bot.get_chat_administrators(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             List of chat members.
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.GET_CHAT_ADMINISTRATORS, json=payload, **kwargs
        )
        members = ChatMember.from_list(response.result, self) or []
        return cast(list[ChatMember], members)

    getChatAdministrators = get_chat_administrators
    """A alias for :meth:`get_chat_administrators`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def download_file(
        self,
        file_id: str,
        destination: str | Path | Callable[[str | bytes], Any] | None = None,
        *,
        chunk_size: int = 64 << 10,
        progress: (
            Callable[[int | None, float], Coroutine[Any, Any, Any] | Any] | None
        ) = None,
        auto_close: bool = False,
        **kwargs,
    ) -> Any:
        """Use this method to Download a file.

        .. code-block:: python

            await bot.download_file("FILE_ID")

        # Arguments:
        #     file_id (:obj:`str`):
        #         Either the file identifier to get file.

        Returns:
             The content of the file
        """
        is_callable = callable(destination) and not hasattr(destination, "write")
        target_file = destination
        internal_open = False

        if destination is None:
            target_file = io.BytesIO()
            write_func = target_file.write
        elif is_callable:
            write_func = destination
        elif isinstance(destination, (str, Path)):
            file_path = Path(destination)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            target_file = file_path.open("wb")
            internal_open = True
            write_func = target_file.write
        elif hasattr(target_file, "write") and callable(getattr(target_file, "write")):
            write_func = target_file.write
        else:
            raise TypeError(
                "destination must have a callable 'write' method or be a callable function."
            )

        try:
            await self._http.download_file(
                file_id,
                cast(Callable[[Any], Any], write_func),
                chunk_size=chunk_size,
                progress=progress,
                **kwargs,
            )
        finally:
            if internal_open:
                target_file.close()  # noqa
            if auto_close and callable(getattr(destination, "close", None)):
                destination.close()  # noqa

        if is_callable:
            return None
        if destination is None:
            return target_file.getvalue()  # noqa
        if isinstance(destination, (str, Path)):
            return Path(destination)

        if not auto_close and callable(getattr(target_file, "seek", None)):
            with suppress(Exception):
                target_file.seek(0)  # noqa

        return target_file

    @arguments_shield
    async def invite_user(
        self, chat_id: str | int, user_id: str | int, **kwargs
    ) -> bool:
        """Use this method to invite a user to the chat.

        .. code-block:: python

            await bot.get_chat(6429983203, 6429983203)

        Arguments:
            chat_id:
                |chat_id|
            user_id:
                Unique identifier for the target user.

        Returns:
             On success, :obj:`True` is returned.
        """
        payload = {"chat_id": chat_id, "user_id": user_id}

        response = await self.request(APIEndpoint.INVITE_USER, json=payload, **kwargs)
        return cast(bool, response.result)

    inviteUser = invite_user
    """A alias for :meth:`invite_user`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def revoke_chat_invite_link(
        self, chat_id: str | int, invite_link: "str | ChatInviteLink", **kwargs
    ) -> str:
        """Use this method to generate a new primary invite link for a chat; any previously generated link is revoked. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights.

        .. code-block:: python

            await bot.revoke_chat_invite_link(6429983203, 'ble.ir/join/79HeEs5FYB')

        Arguments:
            chat_id:
                |chat_id|
            invite_link:
                The invite link to revoke.

        Returns:
             New invite link on success.

        .. versionadded:: 3.0
        """
        if isinstance(invite_link, ChatInviteLink):
            invite_link = invite_link.invite_link

        payload = {"chat_id": chat_id, "invite_link": invite_link}

        response = await self.request(
            APIEndpoint.REVOKE_CHAT_INVITE_LINK, json=payload, **kwargs
        )
        invite_link = ChatInviteLink.from_dict(response.data).invite_link  # noqa
        return invite_link

    revokeChatInviteLink = revoke_chat_invite_link
    """A alias for :meth:`revoke_chat_invite_link`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def create_chat_invite_link(
        self, chat_id: str | int, **kwargs
    ) -> "ChatInviteLink":
        """Use this method to create an additional invite link for a chat. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. The link can be revoked using the method :meth:`revoke_chat_invite_link`.

        .. code-block:: python

            await bot.create_chat_invite_link(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             New invite link on success.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.CREATE_CHAT_INVITE_LINK, json=payload, **kwargs
        )
        invite_link = ChatInviteLink.from_dict(response.result)
        return cast(ChatInviteLink, invite_link)

    createChatInviteLink = create_chat_invite_link
    """A alias for :meth:`create_chat_invite_link`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def export_chat_invite_link(self, chat_id: str | int, **kwargs) -> str:
        """Use this method to generate a new primary invite link for a chat; any previously generated link is revoked. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights.

        .. code-block:: python

            await bot.export_chat_invite_link(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             New invite link on success.

        .. versionadded:: 3.0
        """
        payload = {"chat_id": chat_id}

        response = await self.request(
            APIEndpoint.EXPORT_CHAT_INVITE_LINK, json=payload, **kwargs
        )
        return cast(str, response.result)

    exportChatInviteLink = export_chat_invite_link
    """A alias for :meth:`export_chat_invite_link`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def leave_chat(self, chat_id: str | int, **kwargs) -> bool:
        """Use this method for your bot to leave a group, channel.

        .. code-block:: python

            await bot.leave_chat(6429983203)

        Arguments:
            chat_id:
                |chat_id|

        Returns:
             On success, :obj:`True` is returned.
        """
        payload = {"chat_id": chat_id}

        response = await self.request(APIEndpoint.LEAVE_CHAT, json=payload, **kwargs)
        return cast(bool, response.result)

    leaveChat = leave_chat
    """A alias for :meth:`leave_chat`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        prices: list[LabeledPrice],
        **kwargs,
    ) -> str:
        """
        Create a new wallet payment invoice for use in `mini-apps <https://docs.bale.ai/miniapp>`_.

        This method generates an `invoice_id` representing an open wallet invoice, which can be used
        in Mini-App payment flows. The generated invoice includes product details and a destination
        provider token (such as a wallet token or card number).

        The :paramref:`payload` is a custom string defined by the bot and returned in the :class:`~bale.SuccessfulPayment` (:attr:`~bale.Message.successful_payment`) update
        after a successful transaction. This field is not shown to the user and is intended for internal use
        such as distinguishing between payment requests.

        For further details, refer to the `openInvoice <https://docs.bale.ai/miniapp#%D9%85%D8%AA%D8%AF%D9%87%D8%A7>`_ section in the Mini-App documentation.

        .. code-block:: python

            await bot.create_invoice_link(
                title="Book",
                description="Digital e-book: 'Python Basics'",
                payload="order-1234",
                provider_token="6037************",
                prices=[
                    LabeledPrice(label="Python Book", amount=120000),
                ]
            )

        Arguments:
            title:
                Name of the product, between 1 to 32 characters.
            description:
                Description of the product, between 1 to 255 characters.
            payload:
                A bot-defined payload (1–128 bytes) used to identify the invoice. **Hidden from the user.**
            provider_token:
                The recipient card number or wallet payment token obtained from `@BotFather <https://ble.ir/BotFather>`_.
            prices:
                A list of labeled prices (product title and amount).

        Returns:
            A unique identifier of the Invoice that can be sent to the client to initiate the payment.

        .. versionadded:: 3.0
        """
        payload = {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "prices": prices,
        }

        response = await self.request(
            APIEndpoint.CREATE_INVOICE_LINK, json=payload, **kwargs
        )
        return cast(str, response.result)

    createInvoiceLink = create_invoice_link
    """A alias for :meth:`create_invoice_link`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def inquire_transaction(self, transaction_id: str, **kwargs) -> "Transaction":
        """Sends a request to inquire the status and details of a specific transaction.

        .. code-block:: python

            await bot.inquire_transaction('TRANSACTION_ID')

        Arguments:
            transaction_id: The unique identifier of the transaction to inquire.

        Returns:
            An object containing transaction details and status.

        Note:
            ⚠️ This method is not part of the standard Telegram bot APIs. It is specific to `Bale <https://ble.ir>`_.

        .. versionadded:: 3.0
        """
        payload = {"transaction_id": transaction_id}

        response = await self.request(
            APIEndpoint.INQUIRE_TRANSACTION, json=payload, **kwargs
        )

        transaction = Transaction.from_dict(response.result)
        return cast(Transaction, transaction)

    inquireTransaction = inquire_transaction
    """A alias for :meth:`inquire_transaction`.
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_webhook_info(self, **kwargs) -> "WebhookInfo":
        """Use this method to get current webhook status.

        .. code-block:: python

            await bot.get_webhook_info()

        Returns:
             The webhook info.

        .. versionadded:: 3.0
        """
        response = await self.request(APIEndpoint.GET_WEBHOOK_INFO, **kwargs)
        webhook_info = WebhookInfo.from_dict(response.result, bot=self)
        return cast(WebhookInfo, webhook_info)

    getWebhookInfo = get_webhook_info
    """A alias for :meth:`get_webhook_info`.
    
    
    .. versionadded:: 3.0
    """

    @arguments_shield
    async def get_updates(
        self,
        *,
        offset: SentinelOrValue[int] = MISSING,
        limit: SentinelOrValue[int] = MISSING,
        timeout: SentinelOrValue[int] = MISSING,
        **kwargs,
    ) -> tuple["Update"]:
        """Use this method to get pending updates.

        .. code-block:: python

            updates = await bot.get_updates()

        Arguments:
            offset:
                Identifier of the first update to be returned. Must be greater by one than the highest among the
                identifiers of previously received updates.
            limit:
                Limits the number of updates to be retrieved. Values between ``1``-``100`` are accepted. Defaults to ``100``.
            timeout:
                The duration (in seconds) to wait in :ref:`get_updates_method`. If no update is received within this period, an empty response will be returned. Using this parameter reduces the number of requests and improves performance.

        .. versionchanged:: 3.0
            The :paramref:`timeout` parameter has been added.
        """
        payload = {"offset": offset, "limit": limit, "timeout": timeout}

        response_result = (
            await self.request(APIEndpoint.GET_UPDATES, json=payload, **kwargs)
        ).result
        updates = Update.from_list(response_result, self)
        return cast(tuple[Update], updates)

    getUpdates = get_updates
    """A alias for :meth:`get_updates`.
    
    .. versionadded:: 3.0
    """

    async def _initialize(self):
        await self.get_me()

        if self.__ready_event is None:
            raise RuntimeError(
                "Bot is not initialized. "
                "Ensure the event loop is running and setup has completed."
            )

        self.__ready_event.set()
        self.dispatch("ready")

    async def _restore_active_flows(self) -> None:
        """Restores and reschedules pending conversation flows from the storage on startup."""
        storage = self.storage
        if storage is None:
            return

        async with self._flows_lock:
            registered_classes = {
                cls._identity(): cls for cls in self._registered_flows
            }
            flows_data = await storage.get_all_flow_data()

            for key, record in flows_data.items():
                flow_name = record.get("flow", None)
                if flow_name in registered_classes:
                    flow_class = cast(
                        Type["ConversationFlow"], registered_classes[flow_name]
                    )  # noqa
                    maybe_flow = await flow_class.restore(key, self._storage, record)

                    if maybe_flow:
                        self._flows.add(maybe_flow)
                    else:
                        await storage.drop_flow_data(key)

    def done_task_callback(self, task: asyncio.Task[Any]) -> None:
        """This function remove an task from :class:`asyncio.Task` (s) set if it is a member."""
        self.__tasks.discard(task)

    def create_task(
        self, coroutine: Coroutine, *, name: str | None = None
    ) -> asyncio.Task[Any]:
        """This function used to make a new asyncio task.

        Arguments:
            coroutine:
                The coroutine to create task.
            name:
                The name of the task.

        Returns:
             The created task.
        """
        task = asyncio.create_task(coroutine, name=name)
        self.__tasks.add(task)
        task.add_done_callback(self.done_task_callback)

        return task

    def get_commands(self) -> list[str]:
        from .handlers import \
            CommandHandler  # pylint: disable=import-outside-toplevel

        commands = []
        for handler in self._handlers:
            if isinstance(handler, CommandHandler):
                for cmd in handler.commands:
                    if cmd not in commands:
                        commands.append(cmd)

        return commands

    async def __run_core_safe(self, core: Coroutine) -> Any:
        try:
            return await core
        except asyncio.CancelledError:
            pass

    async def process_handler(
        self, handler: "UpdateHandler", context: "Context"
    ) -> None:
        if returned_args := await handler.check_new_update(context):
            core = handler.handle_update(context, *returned_args)
            await self.__run_core_safe(core)

    async def process_middlewares_before(self, context: "Context") -> bool:
        async def wrapper(middleware: "BaseMiddleware") -> bool:
            # convert Middlewares to boolean type
            flag = await middleware.before_update(context)

            if not isinstance(flag, bool):
                raise MiddlewareError(
                    mw,
                    f"The global check finally must returned a boolean type, not {type(flag).__name__}",
                )

            return flag

        for mw in self._middlewares:
            try:
                flag = await wrapper(mw)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.dispatch("middleware_process_error", exc)
                flag = False

            if not flag:
                return False

        return True

    async def process_middlewares_after(self, context: "Context") -> None:
        for mw in self._middlewares:
            with suppress(Exception):
                await mw.after_update(context)

    async def _process_handler_safe(
        self, context: "Context", handler: "UpdateHandler"
    ) -> None:
        try:
            await self.process_handler(handler, context)
        except asyncio.CancelledError:
            pass
        except Exception as exc:  # pylint: disable=broad-exception-caught
            try:
                self.dispatch("process_handler_error", handler, context, exc)
            except asyncio.CancelledError:
                pass

    async def process_handlers(self, context: "Context") -> None:
        handlers = self._handlers

        for handler in handlers:
            self.create_task(
                self._process_handler_safe(context, handler),
                name=f"Bot:process_handler:{context.update.update_id}:{handler}",
            )

    async def process_flow(
        self, context: Context, flow: "ConversationFlow"
    ) -> bool | None:
        core = flow.invoke(context)
        return await self.__run_core_safe(core)

    async def process_flows(self, context: "Context") -> bool:
        async with self._flows_lock:
            flows = list(self._flows)  # copy

        invoke_handlers = MISSING
        tasks = [self.process_flow(context, flow) for flow in flows]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        flows_to_remove = []

        for flow, result in zip(flows, results):
            if isinstance(result, Exception):
                if isinstance(result, FlowBadStatusError):
                    if await flow.is_dead():
                        flows_to_remove.append(flow)
                        continue

                _log.error(
                    "Error occurred while processing flow %r: %s",
                    flow,
                    result,
                    exc_info=result,
                )
                continue
            elif isinstance(result, bool) and invoke_handlers is not False:
                invoke_handlers = result
            else:
                _log.warning(
                    "Unexpected return type from process_flow for %r: expected bool, got %r (%s)",
                    flow,
                    result,
                    type(result).__name__,
                )

        async with self._flows_lock:
            for dead_flow in flows_to_remove:
                self._flows.discard(dead_flow)

        return invoke_handlers is not False

    async def create_context(self, update):
        kwargs = {}
        if self._storage:
            kwargs["storage"] = self._storage

        return Context.from_update(update, **kwargs)

    async def process_new_update(self, update: "Update") -> None:
        """This is the first function called after the system encounters an update. During the invocation of this function, the following actions are performed simultaneously:

        -	Calling all handlers for the :func:`on_update` event.
        -	Calling all handlers whose :meth:`UpdateHandler.check_new_update <bale.handlers.UpdateHandler.check_new_update>` method returns an acceptable output.
        -	Completing the process for listeners where at least one of their checks aligns with the update (their :meth:`Check.check_update <bale.checks.Check.check_update>` method returns an acceptable response).

        Arguments:
            update:
                The received update object.

        """
        _log.debug("Processing update %s", update)
        self.dispatch("raw_update", update)

        context = await self.create_context(update)

        allowed: bool = await self.process_middlewares_before(context)
        if not allowed:
            return

        self.dispatch("update", update)

        run_handlers = True
        if self._flows:
            run_handlers = await self.process_flows(context)

        if run_handlers:
            await self.process_handlers(context)

        await self.process_middlewares_after(context)

    async def _process_update_wrapper(self, update: "Update"):
        await self.process_new_update(update)
        self.update_queue.task_done()

    async def __updater_fetcher(self) -> None:
        while True:
            try:
                item = await self.update_queue.get()
                if item is STOP_UPDATER_MARKER:
                    while not self.update_queue.empty():
                        self.update_queue.task_done()

                    self.update_queue.task_done()  # for the marker
                    return

                item: "Update"
                self.create_task(
                    self._process_update_wrapper(item),
                    name=f"Bot:updater_fetcher:process_update:{item.update_id}",
                )
            except asyncio.CancelledError:
                _log.warning("The update fetcher can only be closed with Bot.close.")

    async def _updater_fetcher_wrapper(self) -> None:
        self.__updater_fetcher_task = self.create_task(
            self.__updater_fetcher(), name="Bot:updater_fetcher"
        )

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_running_loop()
        except (
            RuntimeError
        ):  # https://github.com/python/cpython/blob/main/Lib/asyncio/events.py#L715-L717
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if platform.system() != "Windows":
            from signal import (  # pylint: disable=import-outside-toplevel
                SIGINT, SIGTERM)

            def raise_system_exit_exc():
                """
                This function raises a SystemExit exception.
                """
                raise SystemExit

            for sig in (SIGINT, SIGTERM):
                loop.add_signal_handler(sig, raise_system_exit_exc)
        return loop

    def __run(
        self,
        startup_coroutines: list[Coroutine],
        operation_coroutine: list[Coroutine],
        cleanup_coroutines: list[Coroutine],
    ) -> None:
        loop = self._get_loop()

        try:
            loop.run_until_complete(loop.create_task(self._setup_hook()))
            loop.run_until_complete(loop.create_task(self._initialize()))
            for coro in startup_coroutines:
                loop.run_until_complete(loop.create_task(coro))
            loop.create_task(self._updater_fetcher_wrapper())
            for op in operation_coroutine:
                loop.create_task(op)
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            _log.debug(
                "The request to stop receiving has been received. Currently in the process of shutting down..."
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            _log.info(
                "We encountered the error, currently in the process of shutting down...",
                exc_info=exc,
            )
        finally:
            for coro in startup_coroutines + operation_coroutine:
                with suppress(Exception):
                    coro.close()
            for coro in cleanup_coroutines:
                loop.run_until_complete(loop.create_task(coro))
            loop.run_until_complete(self.close())

    def run(
        self,
        /,
        skip_updates: bool = False,
        log_handler: logging.Handler | None = None,
        log_level: int = logging.INFO,
        log_format: str | None = None,
        startup_coroutines: list[Coroutine] | None = None,
        cleanup_coroutines: list[Coroutine] | None = None,
        updater_error_handler: Callable[[Exception], bool] | None = None,
        get_updates_timeout: int = DEFAULT_GET_UPDATES_TIMEOUT,
    ):
        """This method is used to run the bot, updater, and update fetcher process.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                ...
                bot = Bot(token="YOUR_TOKEN")

                bot.run() # to run the bot

        Arguments:
            skip_updates:
                Whether to drop pending updates accumulated while the bot was offline before
                starting the polling process. Defaults to ``False``.
            log_handler:
                A logging handler to use for logging. If provided, the class will use this handler for logging
                operations. Defaults to :class:`logging.StreamHandler`.
            log_level:
                The logging level to be used for logging. If provided, the class will use this level for logging
                operations. Defaults to :obj:`logging.INFO`.
            log_format:
                The format string to use for formatting log messages. If provided, the class will use this for logging
                messages. Defaults to ``%Y-%m-%d %H:%M:%S``.
            startup_coroutines:
                A tuple of functions to be executed (for async functions using :obj:`asyncio.loop.run_until_complete` method
                for execute) when the class is starting to run. Defaults to :obj:`None`.
            cleanup_coroutines:
                A tuple of functions to be executed (for async functions using :obj:`asyncio.loop.run_until_complete` method
                for execute) when the class is Terminating work. Defaults to :obj:`None`.
            updater_error_handler:
                This function is called when an error occurs in the updater. The function should have a parameter to receive the updater error. The return value of this function is :obj:`bool` and indicates whether the updater can continue or not.

                This function should be written as follows:

                .. code-block:: python

                    from bale import BaleError

                    def getupdates_error_handler(exc: Exception) -> bool:
                        if isinstance(exc, BaleError):
                            return False
                        return True

            get_updates_timeout:
                The duration (in seconds) to wait in long polling mode. If no update is received
                within this period, an empty response will be returned. Using this parameter reduces
                the number of requests and improves performance.

                This parameter affects the updater's waiting behavior for new updates.

        .. versionchanged:: 3.0
            The :paramref:`skip_updates`, :paramref:`getupdates_error_handler` & :paramref:`getupdates_timeout` parameters has been added.
        """
        if not self.is_closed():
            raise RuntimeError(
                "The bot is not closed! You cannot run a unclosed bot instance."
            )

        setup_logging(handler=log_handler, level=log_level, formatter=log_format)
        operation_coro: list[Coroutine[Any, Any, Any]] = []
        startup_coro: list[Coroutine[Any, Any, Any]] = startup_coroutines or []
        cleanup_coro: list[Coroutine[Any, Any, Any]] = cleanup_coroutines or []

        if updater := self._updater:
            startup_coro.append(updater.setup())
            operation_coro.append(
                updater.start_polling(
                    get_updates_timeout=get_updates_timeout,
                    error_handler=updater_error_handler,
                    skip_updates=skip_updates,
                )
            )
            cleanup_coro.append(updater.stop())

        if storage := self._storage:
            startup_coro.append(storage.initialize())
            startup_coro.append(self._restore_active_flows())
            cleanup_coro.append(storage.close())

        self.__run(
            startup_coroutines=startup_coro,
            operation_coroutine=operation_coro,
            cleanup_coroutines=cleanup_coro,
        )
