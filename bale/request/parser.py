from aiohttp import ClientResponse
from typing import Any
from json import loads
from json.decoder import JSONDecodeError
from ..error import HTTPClientError

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

	@classmethod
	async def from_response(cls, data: "ClientResponse"):
		if data.status == 404:
			return cls(False, raw=dict())

		_data = await data.text()

		try:
			data = loads(_data)
		except JSONDecodeError:
			return cls(False, description=_data, raw=dict(description=HTTPClientError.RATE_LIMIT))
		else:
			return cls(data.get("ok", False), data.get("result"), data.get("error_code"), data.get("description"), data)
