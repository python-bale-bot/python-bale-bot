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
from typing import Any, Type, TYPE_CHECKING, Optional, Dict
from bale.utils.types import MissingValue
import json

if TYPE_CHECKING:
    from bale.request import ResponseParser
    from bale._error import BaleError

__all__ = (
    "ResponseStatusCode",
    "to_json",
    "find_error_class",
    "handle_request_payload"
)


class ResponseStatusCode:
    OK = 200
    NOT_INCORRECT = 400
    NOT_FOUND = 440
    PERMISSION_DENIED = 403
    RATE_LIMIT = 429


def to_json(obj: Any) -> str:
    return json.dumps(obj)


def find_error_class(response: "ResponseParser") -> Optional[Type["BaleError"]]:
    from bale._error import __ERROR_CLASSES__

    for err_obj in __ERROR_CLASSES__:
        if err_obj.STATUS_CODE == response.original_response.status or err_obj.check_response(response):
            return err_obj

    return None


def handle_request_payload(payload: Dict[str, Any] = None):
    payload = {
        key: value.to_json() if hasattr(value, 'to_json') else value
        for key, value in payload.items() if value is not MissingValue
    }
    return payload
