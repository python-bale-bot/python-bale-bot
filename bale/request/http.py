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
from bale.version import BALE_API_BASE_URL, BALE_API_FILE_URL
import asyncio
import aiohttp
from ..error import (NetworkError, TimeOut, NotFound, Forbidden, APIError, BaleError, HTTPClientError, RateLimited, HTTPException)
from .parser import ResponseParser
from .utils import ResponseStatusCode
from collections import deque

__all__ = ("HTTPClient", "Route")


class RateLimit:
	__slots__ = (
		"_loop",
		"_requests",
		"_has_rate_limit"
	)
	def __init__(self, loop):
		self._has_rate_limit = False
		self._requests = deque()
		self._loop = loop

	def enable(self):
		self._has_rate_limit = True

	def _next(self):
		while self._requests:
			future = self._requests.popleft()

			if not future.done():
				future.set_result(None)
				break

	def _wake(self):
		while self._requests:
			future = self._requests.popleft()
			if not future.done():
				future.set_result(None)

	async def new_request(self):
		if self._has_rate_limit:
			future = self._loop.create_future()
			self._requests.append(future)

			try:
				await future
			except:
				future.cancel()
				if not self._has_rate_limit:
					self._next()
				raise

	async def __aenter__(self):
		await self.new_request()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if len(self._requests) > 0:
			self._next()
		else:
			self._has_rate_limit = False

	def __bool__(self):
		return self._has_rate_limit

class Route:
	"""Route Class for http"""
	__slots__ = (
		"method",
		"path",
		"token",
		"_base"
	)

	def __init__(self, method: str, path: str, token: str):
		if not isinstance(token, str):
			raise TypeError("token param must be str.")
		self.method = method
		self.path = path
		self.token = token
		self._base = BALE_API_BASE_URL

	@property
	def url(self):
		"""finally url"""
		return self._base + "bot" + self.token + "/" + self.path

	def set_base(self, _value):
		"""Set base url for route"""
		self._base = _value

class HTTPClient:
	"""Send a Request to BALE API Server"""

	__slots__ = (
		"_loop",
		"token",
		"__session",
		"rate_limit",
		"base_url"
	)

	def __init__(self, loop, token=None, base_url = None):
		self.__session = None
		self._loop: asyncio.AbstractEventLoop = loop
		self.token = token
		self.rate_limit = RateLimit(self.loop)
		self.base_url: str = base_url

	def is_closed(self):
		return self.__session is None

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, _value):
		self._loop = _value
		self.rate_limit._loop = _value

	def reload_session(self):
		"""Reset Session"""
		if self.__session and self.__session.closed:
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def start(self):
		"""Start Http client"""
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def close(self):
		"""Close Session connection"""
		if self.__session:
			await self.__session.close()
			self.__session = None

	async def request(self, route: Route, **kwargs):
		if self.base_url:
			route.set_base(self.base_url)
		url = route.url
		method = route.method
		async with self.rate_limit:
			for tries in range(5):
				try:
					async with self.__session.request(method=method, url=url, **kwargs) as response:
						response: aiohttp.ClientResponse = response
						parsed_response = await ResponseParser.from_response(response)
						if response.status == ResponseStatusCode.OK:
							return parsed_response
						elif response.status == ResponseStatusCode.NOT_FOUND:
							raise NotFound(parsed_response.description)
						elif response.status == ResponseStatusCode.PERMISSION_DENIED:
							raise Forbidden()
						elif not parsed_response.ok or response.status in (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.RATE_LIMIT):
							if parsed_response.description == HTTPClientError.USER_OR_CHAT_NOT_FOUND:
								raise NotFound("User or Chat not Found")
							elif response.status == ResponseStatusCode.RATE_LIMIT or parsed_response.description in (HTTPClientError.RATE_LIMIT, HTTPClientError.LOCAL_RATE_LIMIT):
								if tries >= 4:
									raise RateLimited()

								if bool(self.rate_limit):
									await self.rate_limit.new_request()
								else:
									self.rate_limit.enable()
									await asyncio.sleep(tries * 2 + 1)
								continue
							elif parsed_response.description == HTTPClientError.PERMISSION_DENIED:
								raise Forbidden()

							raise APIError(
									str(parsed_response.error_code), parsed_response.description
								)
				except aiohttp.ClientConnectorError as error:
					raise NetworkError(str(error))
				except aiohttp.ServerTimeoutError:
					raise TimeOut()
				except aiohttp.ClientOSError as error:
					raise BaleError(str(error))
				except Exception as error:
					raise HTTPException(error)

	async def get_file(self, file_id):
		async with self.__session.get(BALE_API_FILE_URL + "/" + "bot" + self.token + "/" + file_id) as response:
			if response.status == ResponseStatusCode.OK:
				return await response.read()
			elif response.status == ResponseStatusCode.NOT_FOUND:
				raise NotFound("Document is not Found")
			elif response.status == ResponseStatusCode.PERMISSION_DENIED:
				raise Forbidden()
			else:
				error_payload = await response.json()
				raise APIError(0, "UNKNOWN ERROR: {}".format(error_payload))

		raise RuntimeError("failed to get file")

	def send_message(self, chat_id, text, *, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"text": text
		}
		if components:
			payload["reply_markup"] = components
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendMessage", self.token), json=payload)

	def forward_message(self, chat_id, from_chat_id, message_id):
		payload = {
			"chat_id": chat_id,
			"from_chat_id": from_chat_id,
			"message_id": message_id
		}

		return self.request(Route("POST", "forwardMessage", self.token), json=payload)

	def send_document(self, chat_id, document, *, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"document": document
		}
		if caption:
			payload["caption"] = caption

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "Senddocument", self.token), data=payload)

	def send_photo(self, chat_id, photo, *, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"photo": photo
		}
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendPhoto", self.token), data=payload)

	def send_audio(self, chat_id, audio, *, caption=None, duration=None, title=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"audio": audio
		}
		if caption:
			payload["caption"] = caption
		if duration:
			payload["duration"] = duration
		if title:
			payload["title"] = title
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendAudio", self.token), data=payload)

	def send_contact(self, chat_id, phone_number, first_name, *, last_name):
		payload = {
			"chat_id": chat_id,
			"phone_number": phone_number,
			"first_name": first_name
		}
		if last_name:
			payload["last_name"] = last_name

		return self.request(Route("POST", "SendContact", self.token), data=payload)

	def send_invoice(self, chat_id, title, description, provider_token, prices, photo_url=None, need_name=False, need_phone_number=False, need_email=False, need_shipping_address=False, is_flexible=True):
		payload = {"chat_id": chat_id, "title": title, "description": description, "provider_token": provider_token, "prices": prices}
		if photo_url:
			payload["photo_url"] = photo_url
		payload["need_name"] = need_name
		payload["need_phone_number"] = need_phone_number
		payload["need_email"] = need_email
		payload["need_shipping_address"] = need_shipping_address
		payload["is_flexible"] = is_flexible

		return self.request(Route("POST", "sendInvoice", self.token), json=payload)

	def send_location(self, chat_id, latitude, longitude):
		payload = { "chat_id": chat_id, "latitude": latitude, "longitude": longitude}

		return self.request(Route("POST", "sendLocation", self.token), json=payload)

	def edit_message(self, chat_id, message_id, text, *, components=None):
		payload = {
			"chat_id": chat_id,
			"message_id": message_id,
			"text": text
		}
		if components:
			payload["reply_markup"] = components

		return self.request(Route("POST", "editMessageText", self.token), json=payload)

	def delete_message(self, chat_id, message_id):
		payload = {
			"chat_id": chat_id,
			"message_id": message_id
		}
		return self.request(Route("GET", "deletemessage", self.token), params=payload)

	def get_updates(self, offset=None, limit=None):
		payload = {}
		if offset:
			payload["offset"] = offset
		if limit:
			payload["limit"] = limit
		return self.request(Route("POST", "getupdates", self.token), json=payload)

	def delete_webhook(self):
		return self.request(Route("GET", "deleteWebhook", self.token))

	def get_bot(self):
		return self.request(Route("GET", "getme", self.token))

	def get_chat(self, chat_id):
		return self.request(Route("GET", "getchat", self.token), params=dict(chat_id=chat_id))

	def leave_chat(self, chat_id):
		return self.request(Route("GET", "leaveChat", self.token), params=dict(chat_id=chat_id))

	def get_chat_administrators(self, chat_id):
		return self.request(Route("GET", "getChatAdministrators", self.token), params=dict(chat_id=chat_id))

	def get_chat_members_count(self, chat_id):
		return self.request(Route("GET", "getChatMemberCount", self.token), params=dict(chat_id=chat_id))

	def get_chat_member(self, chat_id, member_id):
		return self.request(Route("GET", "getChatMember", self.token), params=dict(chat_id=chat_id, user_id=member_id))

	def ban_chat_member(self, chat_id, member_id):
		return self.request(Route("POST", "banChatMember", self.token), params=dict(chat_id=chat_id, user_id=member_id))

	def invite_to_chat(self, chat_id, user_id):
		return self.request(Route("GET", "InviteUser", self.token), json=dict(chat_id=chat_id, user_id=user_id))
