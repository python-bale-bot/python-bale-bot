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
from typing import Dict, List, Any
from bale.version import BALE_API_BASE_URL, BALE_API_FILE_URL
import asyncio, aiohttp, logging
from ..error import (NetworkError, TimeOut, NotFound, Forbidden, APIError, BaleError, HTTPClientError, RateLimited, HTTPException)
from ssl import SSLCertVerificationError
from .parser import ResponseParser
from .params import RequestParams
from bale.utils.request import ResponseStatusCode, to_json

__all__ = ("HTTPClient", "Route")

_log = logging.getLogger(__name__)

class Route:
	__slots__ = (
		"base_url",
		"method",
		"endpoint",
		"token"
	)

	def __init__(self, method: str, endpoint: str, token: str):
		if not isinstance(token, str):
			raise TypeError("token param must be str.")
		self.base_url = BALE_API_BASE_URL
		self.method = method
		self.endpoint = endpoint
		self.token = token

	@property
	def url(self):
		return "{base_url}bot{token}/{endpoint}".format(base_url = self.base_url, token = self.token, endpoint = self.endpoint)

def parse_form_data(value: Any):
	if isinstance(value, int):
		value = str(value)
	return value

class HTTPClient:
	"""Send a Request to BALE API Server"""

	__slots__ = (
		"_loop",
		"token",
		"__session",
		"__extra"
	)

	def __init__(self, loop: asyncio.AbstractEventLoop, token: str, /, **kwargs):
		if not isinstance(token, str):
			raise TypeError(
				"token param must be type of str."
			)
		self.__session = None
		self._loop = loop
		self.token = token
		self.__extra = kwargs

	@property
	def user_agent(self) -> str:
		return "python-bale-bot (https://python-bale-bot.ir): An API wrapper for Bale written in Python"

	def is_closed(self) -> bool:
		return self.__session is None

	@property
	def loop(self) -> asyncio.AbstractEventLoop:
		return self._loop

	@loop.setter
	def loop(self, _value):
		self._loop = _value

	def reload_session(self):
		if self.__session and self.__session.closed:
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0, **self.__extra))

	async def start(self):
		if self.__session:
			raise RuntimeError("HTTPClient has already started.")
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0, **self.__extra))

	async def close(self):
		if self.__session:
			await self.__session.close()
			self.__session = None

	async def request(self, route: Route, *, form: List[Dict] = None, **kwargs):
		url = route.url
		method = route.method
		headers = { 'User-Agent': self.user_agent }

		if 'json' in kwargs:
			headers['Content-Type'] = 'application/json'
			kwargs['data'] = to_json(kwargs.pop('json'))


		if form:
			form_data = aiohttp.FormData()
			for file_payload in form:
				form_data.add_field(**file_payload, content_type="multipart/form-data")
			if 'data' in kwargs:
				_data = kwargs.pop('data')
				for param in _data:
					form_data.add_field(param, parse_form_data(_data[param]))

			kwargs['data'] = form_data

		kwargs['headers'] = headers

		for tries in range(1, 5):
			try:
				async with self.__session.request(method=method, url=url, **kwargs) as original_response:
					original_response: aiohttp.ClientResponse
					response: ResponseParser = await ResponseParser.from_response(original_response)
					if original_response.status == ResponseStatusCode.OK:
						return response
					elif not response.ok or original_response.status in (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.RATE_LIMIT):
						if original_response.status == ResponseStatusCode.RATE_LIMIT or response.description in (HTTPClientError.RATE_LIMIT, HTTPClientError.LOCAL_RATE_LIMIT):
							if tries >= 4:
								raise RateLimited()

							await asyncio.sleep(tries * 2)
							continue

						response.get_error()

					elif original_response.status == ResponseStatusCode.NOT_FOUND:
						raise NotFound(response.description)
					elif original_response.status == ResponseStatusCode.PERMISSION_DENIED:
						raise Forbidden()

					raise APIError(response.error_code, response.description)

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

	async def get_file(self, file_id):
		async with self.__session.get("{base_file_url}/bot{token}/{file_id}".format(base_file_url = BALE_API_FILE_URL, token = self.token, file_id = file_id)) as response:
			if response.status == ResponseStatusCode.OK:
				return await response.read()
			elif response.status in (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.NOT_FOUND):
				raise NotFound("File is not Found")
			elif response.status == ResponseStatusCode.PERMISSION_DENIED:
				raise Forbidden()
			else:
				error_payload = await response.json()
				raise APIError(0, "UNKNOWN ERROR: {}".format(error_payload))

		raise RuntimeError("failed to get file")

	def send_message(self, *, params: RequestParams):
		return self.request(Route("POST", "sendMessage", self.token), json=params.payload)

	def forward_message(self, *, params: RequestParams):
		return self.request(Route("POST", "forwardMessage", self.token), json=params.payload)

	def send_document(self, *, params: RequestParams):
		return self.request(Route("POST", "sendDocument", self.token), data=params.payload, form=params.multipart)

	def send_photo(self, *, params: RequestParams):
		return self.request(Route("POST", "SendPhoto", self.token), data=params.payload, form=params.multipart)

	def send_media_group(self, *, params: RequestParams):
		return self.request(Route("POST", "SendMediaGroup", self.token), data=params.payload, form=params.multipart)

	def send_video(self, *, params: RequestParams):
		return self.request(Route("POST", "sendVideo", self.token), data=params.payload, form=params.multipart)

	def send_audio(self, *, params: RequestParams):
		return self.request(Route("POST", "SendAudio", self.token), data=params.payload, form=params.multipart)

	def send_contact(self, *, params: RequestParams):
		return self.request(Route("POST", "sendContact", self.token), data=params.payload, form=params.multipart)

	def send_invoice(self, *, params: RequestParams):
		return self.request(Route("POST", "sendInvoice", self.token), json=params.payload)

	def send_location(self, *, params: RequestParams):
		return self.request(Route("POST", "sendLocation", self.token), json=params.payload)

	def send_animation(self, *, params: RequestParams):
		return self.request(Route("POST", "sendAnimation", self.token), data=params.payload, form=params.multipart)

	def edit_message(self, *, params: RequestParams):
		return self.request(Route("POST", "editMessageText", self.token), json=params.payload)

	def delete_message(self, *, params: RequestParams):
		return self.request(Route("GET", "deleteMessage", self.token), json=params.payload)

	def get_updates(self, *, params: RequestParams):
		return self.request(Route("POST", "getUpdates", self.token), json=params.payload)

	def delete_webhook(self):
		return self.request(Route("GET", "deleteWebhook", self.token))

	def set_webhook(self, *, params: RequestParams):
		return self.request(Route("POST", "setWebhook", self.token), json=params.payload)

	def get_bot(self):
		return self.request(Route("GET", "getMe", self.token))

	def get_chat(self, *, params: RequestParams):
		return self.request(Route("GET", "getChat", self.token), json=params.payload)

	def leave_chat(self, *, params: RequestParams):
		return self.request(Route("GET", "leaveChat", self.token), json=params.payload)

	def get_chat_administrators(self, *, params: RequestParams):
		return self.request(Route("GET", "getChatAdministrators", self.token), json=params.payload)

	def get_chat_members_count(self, *, params: RequestParams):
		return self.request(Route("GET", "getChatMemberCount", self.token), json=params.payload)

	def get_chat_member(self, *, params: RequestParams):
		return self.request(Route("GET", "getChatMember", self.token), json=params.payload)

	def ban_chat_member(self, *, params: RequestParams):
		return self.request(Route("POST", "banChatMember", self.token), json=params.payload)

	def invite_to_chat(self, *, params: RequestParams):
		return self.request(Route("GET", "inviteUser", self.token), json=params.payload)
