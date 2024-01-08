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
from typing import NamedTuple, Optional, Dict, Any, List

__all__ = (
    "RequestParams",
    "handle_request_param"
)

class RequestParams(NamedTuple):
    payload: Optional[Dict[str, Any]]
    multipart: Optional[List[Dict[str, Any]]]

def handle_payload_param(payload: Dict[str, Any]) -> Dict[str, Any]:
    _payload = {}
    for element in payload.keys():
        if payload[element] is not None:
            _payload[element] = payload[element]

    return _payload

def handle_request_param(payload: Dict[str, Any]=None, form: List[Dict[str, Any]]=None):
    return RequestParams(payload=handle_payload_param(payload), multipart=form)