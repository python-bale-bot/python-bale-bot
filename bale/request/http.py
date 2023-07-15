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
from typing import List
from bale.version import BALE_API_BASE_URL, BALE_API_FILE_URL
import asyncio
import aiohttp
from ..attachments import InputFile
from ..error import (NetworkError, TimeOut, NotFound, Forbidden, APIError, BaleError, HTTPClientError, RateLimited, HTTPException, InvalidToken)
from .parser import ResponseParser
from .utils import ResponseStatusCode, to_json

__all__ = ("HTTPClient", "Route")

class Route:
	"""Route Class for http"""
	__slots__ = (
		"method",
		"endpoint",
		"token"
	)

	def __init__(self, method: str, endpoint: str, token: str):
		if not isinstance(token, str):
			raise TypeError("token param must be str.")
		self.method = method
		self.endpoint = endpoint
		self.token = token

	@property
	def url(self):
		"""export url for request"""
		return "{base_url}bot{token}/{endpoint}".format(base_url = BALE_API_BASE_URL, token = self.token, endpoint = self.endpoint)

class HTTPClient:
	"""Send a Request to BALE API Server"""

	__slots__ = (
		"_loop",
		"token",
		"__session"
	)

	def __init__(self, loop, token):
		self.__session = None
		self._loop: asyncio.AbstractEventLoop = loop
		self.token = token

	@property
	def user_agent(self) -> str:
		return "python-bale-bot (https://python-bale-bot.ir): An API Wrapper for Python"

	def is_closed(self):
		return self.__session is None

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, _value):
		self._loop = _value

	def reload_session(self):
		"""Reset Session"""
		if self.__session and self.__session.closed:
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def start(self):
		"""Start Http client"""
		if self.__session:
			raise RuntimeError("HTTPClient started ")
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def close(self):
		"""Close Session connection"""
		if self.__session:
			await self.__session.close()
			self.__session = None

	async def request(self, route: Route, *, form: List[InputFile] = None, **kwargs):
		url = route.url
		method = route.method
		headers = { 'User-Agent': self.user_agent }

		if 'json' in kwargs:
			headers['Content-Type'] = 'application/json'
			kwargs['data'] = to_json(kwargs.pop('json'))

		try:
			data = kwargs.pop('data')
		except KeyError:
			data = None

		if form:
			form_data = aiohttp.FormData()
			for file in form:
				form_data.add_field(**dict(**file.to_dict(), content_type = 'multipart/form-data'))
			if data:
				for param in data:
					form_data.add_field(param, data[param])

			kwargs['data'] = form_data

		kwargs['headers'] = headers

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

							await asyncio.sleep((1 + tries) * 2)
							continue
						elif parsed_response.description == HTTPClientError.PERMISSION_DENIED:
							raise Forbidden()
						elif parsed_response.description == HTTPClientError.TOKEN_NOT_FOUND:
							raise InvalidToken()

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

	def send_document(self, chat_id, document, *, file_name=None, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
		}
		if caption:
			payload["caption"] = caption

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendDocument", self.token), data=payload, form=[InputFile('document', file_name, document)])

	def send_photo(self, chat_id, photo, *, file_name=None, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"photo": photo
		}
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendPhoto", self.token), data=payload, form=[InputFile('photo', file_name, photo)])

	def send_video(self, chat_id, video, *, file_name=None, caption=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id,
			"video": video
		}
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendVideo", self.token), data=payload, form=[InputFile('video', file_name, video)])

	def send_audio(self, chat_id, audio, *, file_name=None, caption=None, duration=None, title=None, reply_to_message_id=None):
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

		return self.request(Route("POST", "SendAudio", self.token), data=payload, form=[InputFile('audio', file_name, audio)])

	def send_contact(self, chat_id, phone_number, first_name, *, last_name):
		payload = {
			"chat_id": chat_id,
			"phone_number": phone_number,
			"first_name": first_name
		}
		if last_name:
			payload["last_name"] = last_name

		return self.request(Route("POST", "sendContact", self.token), data=payload)

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
		return self.request(Route("GET", "deleteMessage", self.token), json=payload)

	def get_updates(self, offset=None, limit=None):
		payload = {}
		if offset:
			payload["offset"] = offset
		if limit:
			payload["limit"] = limit
		return self.request(Route("POST", "getUpdates", self.token), json=payload)

	def delete_webhook(self):
		return self.request(Route("GET", "deleteWebhook", self.token))

	def get_bot(self):
		return self.request(Route("GET", "getMe", self.token))

	def get_chat(self, chat_id):
		return self.request(Route("GET", "getChat", self.token), json=dict(chat_id=chat_id))

	def leave_chat(self, chat_id):
		return self.request(Route("GET", "leaveChat", self.token), json=dict(chat_id=chat_id))

	def get_chat_administrators(self, chat_id):
		return self.request(Route("GET", "getChatAdministrators", self.token), json=dict(chat_id=chat_id))

	def get_chat_members_count(self, chat_id):
		return self.request(Route("GET", "getChatMemberCount", self.token), json=dict(chat_id=chat_id))

	def get_chat_member(self, chat_id, member_id):
		return self.request(Route("GET", "getChatMember", self.token), json=dict(chat_id=chat_id, user_id=member_id))

	def ban_chat_member(self, chat_id, member_id):
		return self.request(Route("POST", "banChatMember", self.token), json=dict(chat_id=chat_id, user_id=member_id))

	def invite_to_chat(self, chat_id, user_id):
		return self.request(Route("GET", "inviteUser", self.token), json=dict(chat_id=chat_id, user_id=user_id))
