from bale.version import BALE_API_BASE_URL
import aiohttp
import asyncio
from ..error import (NetworkError, HTTPException, TimeOut, NotFound, Forbidden, APIError)

__all__ = (
	"HTTPClient"
)


class Route:
	"""
		Args:
			method (str): Request Method
			path (str): Request Path
			token (str): Bot Token
	"""
	BASE = BALE_API_BASE_URL

	__slots__ = (
		"method",
		"path",
		"url",
		"token"
	)

	def __init__(self, method: str, path: str, token: str = None):
		self.url = self.BASE
		if token is not None:
			self.url += token
		self.url += path
		self.method = method
		self.path = path


class HTTPClient:
	"""Send a Request to BALE API Server"""

	__slots__ = (
		"loop",
		"connector",
		"token",
		"__session",
		"conn_timeout",
		"read_timeout"
	)

	def __init__(self, loop=None, connector=None, token=None, conn_timeout=None, read_timeout=None):
		self.loop = loop if loop is not None else asyncio.get_event_loop()
		self.connector = connector
		self.token = token
		self.__session = aiohttp.ClientSession(connector=self.connector)
		self.conn_timeout = conn_timeout if conn_timeout is not None else 300.0
		self.read_timeout = read_timeout if read_timeout is not None else 300.0

	def reload_session(self):
		if self.__session.closed:
			self.__session = aiohttp.ClientSession(connector=self.connector)

	async def request(self, route: Route, **kwargs):
		url = route.url
		method = route.method

		if "json" in kwargs:
			kwargs["data"] = kwargs.pop("json")

		if not kwargs.get("conn_timeout"):
			kwargs["conn_timeout"] = self.conn_timeout

		if not kwargs.get("read_timeout"):
			kwargs["read_timeout"] = self.read_timeout

		try:
			async with self.__session.request(method=method, url=url, **kwargs) as response:
				response: aiohttp.ClientResponse = response
				payload = await response.json()
				if response.status == 200:
					if not payload.get("ok"):
						raise APIError(
							str(payload.get("error_code")) + payload.get("description")
						)
					return response, payload
				elif response.status == 404:
					raise NotFound()
				elif response.status == 403:
					raise Forbidden()
				else:
					raise HTTPException(response, response.json())
		except aiohttp.client_exceptions.ClientConnectorError as error:
			raise NetworkError(error)
		except aiohttp.client_exceptions.ServerTimeoutError:
			raise TimeOut()

		# raise HTTPException(response, response.json())

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
		return self.request(Route("GET", "deletemessage", self.token), json=payload)

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
		return self.request(Route("GET", "getchat", self.token), json=dict(chat_id=chat_id))

	def get_chat_administrators(self, chat_id):
		return self.request(Route("GET", "getChatAdministrators", self.token), json=dict(chat_id=chat_id))

	def get_chat_members_count(self, chat_id):
		return self.request(Route("GET", "getChatAdministrators", self.token), json=dict(chat_id=chat_id))

	def get_chat_member(self, chat_id, member_id):
		return self.request(Route("GET", "getChatMember", self.token), json=dict(chat_id=chat_id, user_id=member_id))
