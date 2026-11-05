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
import asyncio
import logging
import sys
import warnings
from typing import TYPE_CHECKING, Any, TypedDict, cast

import aiohttp

from ._exceptions import RateLimited
from ._message import Message
from ._request import BaleResponse, HTTPClient, Route
from ._user import User
from ._utils import request as utils_request
from ._utils import token as _token
from ._utils.files import parse_file_input
from ._utils.typehint import MISSING, SentinelOrValue
from ._utils.typehint_manager import arguments_shield
from .attachments import Audio, Document, PhotoSize, Video
from .constants import BALE_API_BUSINESS_URL, APIEndpoint

if TYPE_CHECKING:
    from bale import InlineKeyboardMarkup, ReplyKeyboardMarkup

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

__all__ = ("BusinessClient",)

_log = logging.getLogger(__name__)
FileInput = str


class BusinessClientOptions(TypedDict, total=False):
    connector_init: dict[str, Any] | None
    http_trace: aiohttp.TraceConfig | None
    proxy: str | None
    proxy_auth: aiohttp.BasicAuth | None


class BusinessClient:
    """

    .. versionadded:: 3.0
    """

    __slots__ = ("_token", "_http", "_closed")

    def __init__(self, token: str, **options: Unpack[BusinessClientOptions]) -> None:
        _token.validate_token(token)

        self._token: str = token

        connector_init: dict[str, Any] | None = options.get("connector_init")
        http_trace: aiohttp.TraceConfig | None = options.get("http_trace")
        proxy: str | None = options.get("proxy")
        proxy_auth: aiohttp.BasicAuth | None = options.get("proxy_auth")
        self._http: HTTPClient = HTTPClient(
            token,
            connector_init=connector_init,
            http_trace=http_trace,
            proxy=proxy,
            proxy_auth=proxy_auth,
        )
        self._closed: bool = True

    @property
    def bot_id(self) -> int | None:
        """:obj:`int`: Unique identifier of the bot, extracted from the bot token."""
        return _token.extract_bot_id(self._token)

    async def request(
        self,
        api_route: APIEndpoint | None = None,
        method: str | None = None,
        endpoint: str | None = None,
        handle_rate_limit: bool = True,
        **kwargs,
    ) -> BaleResponse:
        """Send an HTTP request to a specified URL using the given method.

        This method is used to send HTTP requests to an API and supports
        various HTTP methods such as GET, POST, PUT, DELETE, etc.

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
            The response object containing the response data.

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

        route = Route(method, endpoint, self._token, base_url=BALE_API_BUSINESS_URL)

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
        """:obj:`bool`: Business client status"""
        return self._closed

    def http_is_closed(self) -> bool:
        """:obj:`bool`: HTTPClient status"""
        return self._http.is_closed()

    async def initialize(self) -> None:
        self._closed = False
        await self._http.start()

    async def __aenter__(self) -> "BusinessClient":
        await self.initialize()
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback) -> None:
        await self.close()
        return None

    async def close(self) -> None:
        """This method closes and releases the bot’s connection to the Bale server and all resources currently in use."""
        if self.is_closed():
            raise RuntimeError("The business client is already closed.")

        if not self.http_is_closed():
            await self._http.close()

        self._closed = True

        _log.info("Closing operation was successfully completed")

    async def get_me(self, **kwargs) -> User:
        """A simple method to test the authentication token of an API.

        Returns:
             Basic information about the bot.
        """
        response = await self.request(APIEndpoint.GET_ME, **kwargs)
        client_user = User.from_dict(data=response.result)
        return cast(User, client_user)

    getMe = get_me

    @arguments_shield
    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        *,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
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
        result = Message.from_dict(data=response.result)

        return cast(Message, result)

    sendMessage = send_message

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
        result = Message.from_dict(data=response.result)
        return cast(Message, result)

    forwardMessage = forward_message

    @arguments_shield
    async def send_document(
        self,
        chat_id: str | int,
        document: "Document | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This method is used to send a file or document to the target chat.

        .. code-block:: python

            await bot.send_document(6429983203, "FILE_ID", caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            document:
                Document file to send. |file_business|
            caption:
                |media_caption|
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "document": parse_file_input(document, Document),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_DOCUMENT, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result)
        return cast(Message, result)

    sendDocument = send_document

    @arguments_shield
    async def send_photo(
        self,
        chat_id: str | int,
        photo: "PhotoSize | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
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

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "photo": parse_file_input(photo, PhotoSize),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_PHOTO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result)
        return cast(Message, result)

    sendPhoto = send_photo

    @arguments_shield
    async def send_audio(
        self,
        chat_id: str | int,
        audio: "Audio | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This service is used to send Audio.

        .. code-block:: python

            await bot.send_audio(6429983203, 'file_id', caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            audio:
                File to send.
            caption:
                Audio caption.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "audio": parse_file_input(audio, Audio),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_AUDIO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result)
        return cast(Message, result)

    sendAudio = send_audio

    @arguments_shield
    async def send_video(
        self,
        chat_id: str | int,
        video: "Video | FileInput",
        *,
        caption: SentinelOrValue[str] = MISSING,
        reply_markup: SentinelOrValue[
            "InlineKeyboardMarkup | ReplyKeyboardMarkup"
        ] = MISSING,
        reply_to_message_id: SentinelOrValue[str | int] = MISSING,
        **kwargs,
    ) -> "Message":
        """This service is used to send Video.

        .. code-block:: python

            await bot.send_video(6429983203, 'file_id', caption = "this is a caption", ...)

        Arguments:
            chat_id:
                |chat_id|
            video:
                File to send.
            caption:
                Video caption.
            reply_markup:
                |reply_markup|
            reply_to_message_id:
                |reply_to_message_id|

        Returns:
            The Message.
        """
        payload = {
            "chat_id": chat_id,
            "video": parse_file_input(video, Video),
            "caption": caption,
            "reply_markup": reply_markup,
            "reply_to_message_id": reply_to_message_id,
        }

        response = await self.request(
            APIEndpoint.SEND_VIDEO, maybe_form_data=payload, **kwargs
        )
        result = Message.from_dict(data=response.result)
        return cast(Message, result)

    sendVideo = send_video
