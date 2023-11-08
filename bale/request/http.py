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
import asyncio
import aiohttp
from ..error import (NetworkError, TimeOut, NotFound, Forbidden, APIError, BaleError, HTTPClientError, RateLimited, HTTPException)
from .parser import ResponseParser
from bale.utils.request import ResponseStatusCode, to_json

__all__ = ("HTTPClient", "Route")

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

	def set_base_url(self, value: Optional[str]):
		if value is not None:
			self.base_url = value

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
		"base_url"
	)

	def __init__(self, loop: asyncio.AbstractEventLoop, token, base_url=None):
		self.__session = None
		self.base_url = base_url
		self._loop = loop
		self.token = token

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
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def start(self):
		if self.__session:
			raise RuntimeError("HTTPClient has already started.")
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(keepalive_timeout=20.0))

	async def close(self):
		if self.__session:
			await self.__session.close()
			self.__session = None

	async def request(self, route: Route, *, form: List[Dict] = None, **kwargs):
		route.set_base_url(self.base_url)
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
				async with self.__session.request(method=method, url=url, **kwargs) as response:
					response: aiohttp.ClientResponse
					parsed_response = await ResponseParser.from_response(response)
					if response.status == ResponseStatusCode.OK:
						return parsed_response
					elif not parsed_response.ok or response.status == (ResponseStatusCode.NOT_INCORRECT, ResponseStatusCode.RATE_LIMIT):
						if response.status == ResponseStatusCode.RATE_LIMIT or parsed_response.description in (HTTPClientError.RATE_LIMIT, HTTPClientError.LOCAL_RATE_LIMIT):
							if tries >= 4:
								raise RateLimited()

							await asyncio.sleep(tries * 2)
							continue

						parsed_response.get_error()

					elif response.status == ResponseStatusCode.NOT_FOUND:
						raise NotFound(parsed_response.description)
					elif response.status == ResponseStatusCode.PERMISSION_DENIED:
						raise Forbidden()

					raise APIError(parsed_response.error_code, parsed_response.description)

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

	def send_document(self, chat_id, form, *, caption=None, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
		}
		if components:
			payload["reply_markup"] = components
		if caption:
			payload["caption"] = caption

		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendDocument", self.token), data=payload, form=form)

	def send_photo(self, chat_id, form, *, caption=None, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
		}
		if components:
			payload["reply_markup"] = components
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendPhoto", self.token), data=payload, form=form)

	def send_media_group(self, chat_id, media):
		payload = {
			"chat_id": chat_id,
			"media": media
		}

		return self.request(Route("POST", "SendMediaGroup", self.token), data=payload)

	def send_video(self, chat_id, form, *, caption=None, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
		}
		if components:
			payload["reply_markup"] = components
		if caption:
			payload["caption"] = caption
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendVideo", self.token), data=payload, form=form)

	def send_audio(self, chat_id, form, *, caption=None, duration=None, title=None, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
		}
		if components:
			payload["reply_markup"] = components
		if caption:
			payload["caption"] = caption
		if duration:
			payload["duration"] = duration
		if title:
			payload["title"] = title
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "SendAudio", self.token), data=payload, form=form)

	def send_contact(self, chat_id, phone_number, first_name, *, last_name):
		payload = {
			"chat_id": chat_id,
			"phone_number": phone_number,
			"first_name": first_name
		}
		if last_name:
			payload["last_name"] = last_name

		return self.request(Route("POST", "sendContact", self.token), data=payload)

	def send_invoice(self, chat_id, title, description, provider_token, prices, payload=None, photo_url=None, need_name=False, need_phone_number=False, need_email=False, need_shipping_address=False, is_flexible=True):
		data = {"chat_id": chat_id, "title": title, "description": description, "provider_token": provider_token, "prices": prices}
		if photo_url:
			data["photo_url"] = photo_url
		if payload:
			data["payload"] = payload
		data["need_name"] = need_name
		data["need_phone_number"] = need_phone_number
		data["need_email"] = need_email
		data["need_shipping_address"] = need_shipping_address
		data["is_flexible"] = is_flexible

		return self.request(Route("POST", "sendInvoice", self.token), json=data)

	def send_location(self, chat_id, latitude, longitude):
		payload = { "chat_id": chat_id, "latitude": latitude, "longitude": longitude}

		return self.request(Route("POST", "sendLocation", self.token), json=payload)

	def send_animation(self, chat_id, form, *, duration=None, width=None, height=None, caption=None, components=None, reply_to_message_id=None):
		payload = {
			"chat_id": chat_id
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
			payload["components"] = components
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id

		return self.request(Route("POST", "sendAnimation", self.token), json=payload, form=form)

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

	def set_webhook(self, url):
		payload = {
			"url": url
		}
		return self.request(Route("POST", "setWebhook", self.token), payload = payload)

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
