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
from json.decoder import JSONDecodeError
from typing import Any

from aiohttp import ClientResponse

from .._utils.object import json as _json
from ._response_parameters import ResponseParameters

__all__ = ("json_or_text", "BaleResponse")


async def json_or_text(response: "ClientResponse") -> Any:
    """Asynchronously processes the response content and attempts to parse it as JSON.
    If parsing as JSON fails, the raw text content is returned.

    Arguments:
        response (:class:`aiohttp.ClientResponse`):
            The response object from which the content will be extracted.

    Returns
        If the response content is valid JSON, returns the parsed JSON object. Otherwise, returns the raw text content of the response.
    """
    text = await response.text()

    try:
        json = _json.loads(text)
    except JSONDecodeError:
        return text
    return json


class BaleResponse:
    """A parser for parse http response.

    Attributes:
        data: dict
            Raw of the response data.

    .. versionadded:: 3.0
    """

    __slots__ = (
        "data",
        "original_response",
        "ok",
        "result",
        "error_code",
        "description",
        "parameters",
    )

    def __init__(self, data: dict[str, Any], response: "ClientResponse") -> None:
        self.data = data
        self.original_response = response
        self.ok = self.data.get("ok", False)
        self.result = self.data.get("result")
        self.error_code = self.data.get("error_code")
        self.description = self.data.get("description")
        self.parameters = ResponseParameters.from_dict(self.data.get("parameters"))

    @classmethod
    async def from_response(cls, response: "ClientResponse"):
        response_data = await json_or_text(response)

        if not isinstance(response_data, dict):
            raise TypeError(f"Non-JSON response: {response_data[:200]}")

        return cls(response_data, response)
