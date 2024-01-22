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
from __future__ import annotations
from typing import Iterable, Callable, TypeVar, Any, Optional
import re
from datetime import datetime

__all__ = (
    "create_deep_linked_url",
    "parse_time",
    "find"
)

T = TypeVar('T')

def create_deep_linked_url(bot_username: str, payload: str) -> str:
    """Creating a deep link for the bot.

    .. warning::
            The username of the robot must be entered in the correct format and invalid characters should not be used in the payload parameter.

    Parameters
    ----------
        bot_username: :class:`str`
            The username of bot.
        payload: :class:`str`
            The Payload of deep link
    """
    if len(bot_username) < 4 or not bot_username.lower().endswith('bot'):
        raise TypeError(
            "bot_username param must be valid username"
        )

    if not re.match(r"^[A-Za-z0-9_-]+$", payload):
        raise TypeError(
            "payload param must be valid payload."
        )

    url = "ble.ir/{username}?start={payload}".format(username = bot_username, payload = payload)
    return url

def parse_time(data: Optional[int]) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(int(data))
    except Exception as exc:
        if not isinstance(exc, (ValueError, TypeError)):
            raise exc
        return None

def find(predicate: Callable[[T], Any], iterable: Iterable[T]) -> Optional[T]:
    """A helper to return the first element in the sequence that meets the predicate.

    Parameters
    ----------
        predicate:
            A function to return boolean-like result.
        iterable: :class:`str`
            An iterable to search through.
    """
    for element in iterable:
        if predicate(element):
            return element

    return None