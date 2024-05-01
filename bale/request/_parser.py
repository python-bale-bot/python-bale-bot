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
from typing import Dict, Any, TYPE_CHECKING
from json import loads
from json.decoder import JSONDecodeError
if TYPE_CHECKING:
    from aiohttp import ClientResponse

async def json_or_text(response: "ClientResponse"):
    text = await response.text()

    try:
        json = loads(text)
    except JSONDecodeError:
        return text
    else:
        return json

class ResponseParser:
    """A parser for parse http response.

    Attributes
    ==========
        data: dict
            Raw of the response data
    """

    __slots__ = (
        "data",
        "original_response"
    )

    def __init__(self, data: Dict[str, Any], response: "ClientResponse"):
        self.data = data
        self.original_response = response

    @property
    def ok(self) -> bool:
        return self.data.get('ok', False)

    @property
    def result(self) -> Any:
        return self.data.get('result')

    @property
    def error_code(self):
        return self.data.get('error_code')

    @property
    def description(self):
        return self.data.get('description')

    @classmethod
    async def parse_response(cls, response: "ClientResponse"):
        fetched_data = await json_or_text(response)

        if not isinstance(fetched_data, dict):
            raise TypeError(
                "The data sent by request cannot be parsed!"
            )

        return cls(fetched_data, response)
