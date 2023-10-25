from aiohttp import ClientResponse
from typing import Any
from json import loads
from json.decoder import JSONDecodeError
from bale.error import HTTPClientError, NotFound, InvalidToken, Forbidden, APIError

async def json_or_text(response: "ClientResponse"):
	text = await response.text()

	try:
		json = loads(text)
	except JSONDecodeError:
		return text
	else:
		return json

class ResponseParser:
	"""a Parser for parse http response.

	Attributes
	==========
	ok: bool
		Status of the response

	result: Any
		Result of the response

	error_code: Optional[:class:`int`]
		Error Code.
		``None`` when no error

	description: Optional[:class:`str`]
		Description of the error.
		``None`` when no error.

	_raw: dict
		Raw of the response data
	"""

	__slots__ = (
		"result",
		"error_code",
		"description",
		"ok",
		"_raw"
	)

	def __init__(self, ok: bool, result: Any = None, error_code: int = None, description: str = None, raw: dict = None):
		self.ok = ok

		self.result = result
		self.error_code = error_code
		self.description = description
		self._raw = raw

	def get_error(self):
		data = {
			HTTPClientError.USER_OR_CHAT_NOT_FOUND: NotFound,
			HTTPClientError.TOKEN_NOT_FOUND: InvalidToken,
			HTTPClientError.PERMISSION_DENIED: Forbidden
		}

		def raise_wrapper():
			raise data.get(self.description, lambda: APIError(self.error_code, self.description))

		return raise_wrapper

	@classmethod
	async def from_response(cls, data: "ClientResponse"):
		data = await json_or_text(data)

		if isinstance(data, str):
			return cls(False, description=data, raw=dict(description=data))
		else:
			return cls(data.get("ok", False), data.get("result"), data.get("error_code"), data.get("description"), data)
