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
from typing import Any, Optional, Type

import asyncio
import aiohttp
import logging
from ssl import SSLCertVerificationError
from .._version import BALE_API_BASE_URL, BALE_API_FILE_URL
from bale.attachments import InputFile
from bale.utils.request import RequestParams
from bale._error import __ERROR_CLASSES__, HTTPClientError, APIError, NetworkError, TimeOut, BaleError, HTTPException
from .parser import ResponseParser

from bale.utils.request import ResponseStatusCode, to_json, find_error_class

__all__ = ("HTTPClient", "Route")

_log = logging.getLogger(__name__)

class Route:
    __slots__ = (
        "base_url",
        "request_method",
        "endpoint",
        "token"
    )

    def __init__(self, request_method: str, endpoint: str, token: str) -> None:
        if not isinstance(token, str):
            raise TypeError("token param must be str.")
        self.base_url = BALE_API_BASE_URL + token
        self.request_method = request_method
        self.endpoint = endpoint
        self.token = token

    @property
    def url(self):
        return f"{self.base_url}/{self.endpoint}"

def parse_form_data(value: Any):
    if isinstance(value, int):
        value = str(value)
    return value

class HTTPClient:
    """Send a Request to BALE API Server"""

    __slots__ = (
        "token",
        "__session",
        "__extra"
    )

    def __init__(self, token: str, /, **kwargs) -> None:
        if not isinstance(token, str):
            raise TypeError(
                "token param must be type of str."
            )

        self.__session = None
        self.token = token
        self.__extra = kwargs

    @property
    def user_agent(self) -> str:
        return "python-bale-bot (https://python-bale-bot.ir): An API wrapper for Bale written in Python"

    def is_closed(self) -> bool:
        return self.__session is None

    def reload_session(self) -> None:
        if self.__session and self.__session.closed:
            self.__session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(keepalive_timeout=20.0, **self.__extra))

    async def start(self) -> None:
        if self.__session:
            raise RuntimeError("HTTPClient has already started.")
        self.__session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(keepalive_timeout=20.0, **self.__extra))

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()
            self.__session = None

    async def request(self, route: Route, *, via_form_data: bool = False, **kwargs) -> ResponseParser:
        url = route.url
        method = route.request_method
        headers = { 'User-Agent': self.user_agent }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = to_json(kwargs.pop('json'))

        if via_form_data:
            form_data = aiohttp.FormData()
            if 'data' in kwargs:
                for key, value in kwargs.pop('data', {}).items():
                    if isinstance(value, InputFile):
                        field_params = value.to_multipart_payload()
                        form_data.add_field(key, **field_params)
                    else:
                        form_data.add_field(key, parse_form_data(value))

            kwargs['data'] = form_data

        kwargs['headers'] = headers

        for tries in range(1, 5):
            try:
                async with self.__session.request(method=method, url=url, **kwargs) as original_response:
                    original_response: aiohttp.ClientResponse
                    _log.debug('[%s] %s with %s has returned %s', method, url, kwargs.get('data'), original_response.status)
                    response = await ResponseParser.parse_response(original_response)
                    if original_response.status == ResponseStatusCode.OK:
                        return response
                    elif not response.ok or original_response.status == ResponseStatusCode.NOT_INCORRECT: # request is done, but is not correct?
                        # so we have to check which of the errors belong to the problem of that request?
                        if original_response.status == ResponseStatusCode.RATE_LIMIT or response.description in (
                            HTTPClientError.RATE_LIMIT, HTTPClientError.LOCAL_RATE_LIMIT
                        ):
                            _log.debug('[%s] %s Received a 429 status code')
                            if tries < 4:
                                await asyncio.sleep(tries * 2)
                                continue

                        error_obj: Optional[Type[BaleError]] = find_error_class(response)
                        if error_obj:
                            raise error_obj(response.description)

                    raise APIError(response.error_code, response.description)

            except SSLCertVerificationError as error:
                _log.warning("Failed connection with ssl. you can set the ssl off.", exc_info=error)
                raise NetworkError(error)
            except aiohttp.ClientConnectorError as error:
                raise NetworkError(error)
            except aiohttp.ServerTimeoutError:
                raise TimeOut()
            except aiohttp.ClientOSError as error:
                raise BaleError(error)
            except BaleError as error:
                raise error
            except Exception as error:
                raise HTTPException(error)

    async def get_file(self, file_id: str):
        base_file_url = BALE_API_FILE_URL + self.token

        try:
            async with self.__session.get(f"{base_file_url}/{file_id}") as original_response:
                if original_response.status == ResponseStatusCode.OK:
                    original_response: aiohttp.ClientResponse
                    return await original_response.read()

                for error_obj in __ERROR_CLASSES__:
                    if error_obj.STATUS_CODE == original_response.status:
                        raise error_obj(None)

                error_payload = await original_response.json()
                raise APIError(error_payload.get('error_code'), error_payload.get('description'))
        except SSLCertVerificationError as error:
            _log.warning("Failed connection with ssl. you can set the ssl off.", exc_info=error)
            raise NetworkError(str(error))
        except aiohttp.ClientConnectorError as error:
            raise NetworkError(str(error))
        except aiohttp.ServerTimeoutError:
            raise TimeOut()
        except aiohttp.ClientOSError as error:
            raise BaleError(str(error))
        except BaleError as error:
            raise error
        except Exception as error:
            raise HTTPException(error)

    def send_message(self, *, params: RequestParams):
        return self.request(Route("POST", "sendMessage", self.token), json=params.payload)

    def forward_message(self, *, params: RequestParams):
        return self.request(Route("POST", "forwardMessage", self.token), json=params.payload)

    def send_document(self, *, params: RequestParams):
        return self.request(Route("POST", "sendDocument", self.token), data=params.payload, via_form_data=True)

    def send_photo(self, *, params: RequestParams):
        return self.request(Route("POST", "SendPhoto", self.token), data=params.payload, via_form_data=True)

    def send_media_group(self, *, params: RequestParams):
        return self.request(Route("POST", "SendMediaGroup", self.token), data=params.payload, via_form_data=True)

    def send_video(self, *, params: RequestParams):
        return self.request(Route("POST", "sendVideo", self.token), data=params.payload, via_form_data=True)

    def send_audio(self, *, params: RequestParams):
        return self.request(Route("POST", "SendAudio", self.token), data=params.payload, via_form_data=True)

    def send_contact(self, *, params: RequestParams):
        return self.request(Route("POST", "sendContact", self.token), data=params.payload)

    def send_invoice(self, *, params: RequestParams):
        return self.request(Route("POST", "sendInvoice", self.token), json=params.payload)

    def send_location(self, *, params: RequestParams):
        return self.request(Route("POST", "sendLocation", self.token), json=params.payload)

    def send_animation(self, *, params: RequestParams):
        return self.request(Route("POST", "sendAnimation", self.token), data=params.payload, via_form_data=True)

    def send_sticker(self, *, params: RequestParams):
        return self.request(Route("POST", "sendSticker", self.token), data=params.payload, via_form_data=True)

    def edit_message_text(self, *, params: RequestParams):
        return self.request(Route("POST", "editMessageText", self.token), json=params.payload)

    def edit_message_caption(self, *, params: RequestParams):
        return self.request(Route("POST", "editMessageCaption", self.token), json=params.payload)

    def copy_message(self, *, params: RequestParams):
        return self.request(Route("POST", "copyMessage", self.token), json=params.payload)

    def delete_message(self, *, params: RequestParams):
        return self.request(Route("GET", "deleteMessage", self.token), json=params.payload)

    def get_updates(self, *, params: RequestParams):
        return self.request(Route("POST", "getUpdates", self.token), json=params.payload)

    def get_webhook_info(self):
        return self.request(Route("GET", "getWebhookInfo", self.token))

    def delete_webhook(self):
        return self.request(Route("GET", "deleteWebhook", self.token))

    def set_webhook(self, *, params: RequestParams):
        return self.request(Route("POST", "setWebhook", self.token), json=params.payload)

    def get_me(self):
        return self.request(Route("GET", "getMe", self.token))

    def get_chat(self, *, params: RequestParams):
        return self.request(Route("GET", "getChat", self.token), json=params.payload)

    def leave_chat(self, *, params: RequestParams):
        return self.request(Route("GET", "leaveChat", self.token), json=params.payload)

    def get_chat_administrators(self, *, params: RequestParams):
        return self.request(Route("GET", "getChatAdministrators", self.token), json=params.payload)

    def get_chat_members_count(self, *, params: RequestParams):
        return self.request(Route("GET", "getChatMembersCount", self.token), json=params.payload)

    def get_chat_member(self, *, params: RequestParams):
        return self.request(Route("GET", "getChatMember", self.token), json=params.payload)

    def set_chat_photo(self, *, params: RequestParams):
        return self.request(Route("POST", "setChatPhoto", self.token), data=params.payload, via_form_data=True)

    def ban_chat_member(self, *, params: RequestParams):
        return self.request(Route("POST", "banChatMember", self.token), json=params.payload)

    def unban_chat_member(self, *, params: RequestParams):
        return self.request(Route("POST", "unbanChatMember", self.token), json=params.payload)

    def invite_user(self, *, params: RequestParams):
        return self.request(Route("GET", "inviteUser", self.token), json=params.payload)

    def promote_chat_member(self, *, params: RequestParams):
        return self.request(Route("POST", "promoteChatMember", self.token), json=params.payload)
