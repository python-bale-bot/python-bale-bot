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

def remove_empty_keys(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {k : v for k, v in payload.items() if v is not None}

def handle_request_param(payload: Dict[str, Any]=None):
    return RequestParams(payload=remove_empty_keys(payload))