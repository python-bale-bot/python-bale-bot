"""
    MIT License

    Copyright (c) 2022 kian Ahmadian

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
from bale.version import BALE_API_BASE_URL
import aiohttp
from ..error import (NetworkError, HTTPException, TimeOut, NotFound, Forbidden, APIError, BaleError)


__all__ = ("HTTPClient", "Route")


class Route:
	"""Route Class for http"""
	BASE = BALE_API_BASE_URL

	__slots__ = (
		"method",
		"path",
		"url",
		"token"
	)

	def __init__(self, method: str, path: str, token: str):
		if not isinstance(token, str):
			raise TypeError("token is not str!\ntoken is a {}".format(token.__class__))
		self.url = self.BASE + "bot" + token + "/" + path
		self.method = method
		self.path = path
		self.token = token


class HTTPClient:
	"""Send a Request to BALE API Server"""

	__slots__ = (
		"loop",
		"token",
		"__session"
	)

	def __init__(self, loop, token=None):
		self.__session = None
		self.loop = loop
		self.token = token

	def reload_session(self):
		"""Reset Session"""
		if self.__session and self.__session.closed:
			self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(limit=0))

	async def start(self):
		"""Start Http client"""
		self.__session = aiohttp.ClientSession(loop=self.loop, connector=aiohttp.TCPConnector(limit=0))

	async def close(self):
		"""Close Session connection"""
		if self.__session:
			await self.__session.close()

	async def request(self, route: Route, **kwargs):
		url = route.url
		method = route.method

		try:
			async with self.__session.request(method=method, url=url, **kwargs) as response:
				response: aiohttp.ClientResponse = response
				if response.status == 200:
					payload = await response.json()
					if not payload.get("ok"):
						raise APIError(
							str(payload.get("error_code")) + payload.get("description")
						)
					return response, payload
				elif response.status == 400:
					payload = await response.json()
					if payload.get("description") == "no such group or user":
						payload = None
						return response, payload
				elif response.status == 404:
					raise NotFound()
				elif response.status == 403:
					raise Forbidden()
				json = await response.json()
				raise HTTPException(response, json)
		except aiohttp.client_exceptions.ClientConnectorError as error:
			raise NetworkError(str(error))
		except aiohttp.client_exceptions.ServerTimeoutError:
			raise TimeOut()
		except aiohttp.client_exceptions.ClientOSError as error:
			raise BaleError(error)

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

	def send_photo(self, chat_id, photo, caption=None):
		payload = {
			"chat_id": chat_id,
			"photo": photo
		}
		if caption:
			payload["caption"] = caption

		return self.request(Route("POST", "SendPhoto", self.token), data=payload)

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

	def edit_message(self, chat_id, message_id, text, components=None):
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
		return self.request(Route("GET", "getChatAdministrators", self.token), params=dict(chat_id=chat_id))

	def get_chat_member(self, chat_id, member_id):
		return self.request(Route("GET", "getChatMember", self.token), params=dict(chat_id=chat_id, user_id=member_id))

	def invite_to_chat(self, chat_id, user_id):
		return self.request(Route("GET", "InviteUser", self.token), json=dict(chat_id=chat_id, user_id=user_id))
