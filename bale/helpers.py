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
from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, TypeVar

from .constants import BALE_BASE_URL

if TYPE_CHECKING:
    from bale import Bot

__all__ = ("parse_time", "find", "create_deep_link", "create_start_link")


PF = TypeVar("PF")


def parse_time(data: str | int | None = None) -> datetime | None:
    """Converts a timestamp into a datetime object.

    Arguments:
        data:
            The timestamp representing the date and time.

    Returns:
         The datetime object.
    """
    if data is not None:
        try:
            return datetime.fromtimestamp(int(data))
        except (ValueError, TypeError):
            pass

    return None


def find(
    predicate: Callable[[PF], bool], iterable: Iterable[Any]
) -> tuple[int, PF] | None:
    """A helper to return the first element in the sequence that meets the predicate.

    Arguments:
        predicate:
            A function to return boolean-like result.
        iterable (:obj:`str`):
            An iterable to search through.

    .. versionadded:: 2.5.0
    """
    for index, element in enumerate(iterable):
        if predicate(element):
            return index, element

    return None


async def create_start_link(bot: "Bot", payload: str) -> str:
    """Creates a start deep link for the given bot.

    This function generates a deep link using the bot's username and the provided payload.
    also serves as a shortcut for :meth:`create_deep_link` with the ``start`` link type.

    .. admonition:: Example Code
        :class: tip

        .. code-block:: python

            from bale import helpers

            link = await helpers.create_start_link(bot, "site")  # https://ble.ir/pbbbot?start=site

    Arguments:
        bot:
            The bot instance from which the username will be fetched.
        payload:
            The payload to be included in the deep link. Must contain only valid characters.

    Returns:
        The generated deep link for the bot.

    .. versionadded:: 3.0
    """
    return create_deep_link(bot, "start", payload)


def create_deep_link(username: "Bot | str", link_type: str, payload: str) -> str:
    """Creating a deep link for the bot.

    .. warning::

        The username of the bot must be entered in the correct format and invalid characters should not be used in the payload parameter.

    .. admonition:: Example Code
        :class: tip

        .. code-block:: python

            from bale import helpers

            link = helpers.create_deep_link('pbbbot', 'start', 'site') # https://ble.ir/pbbbot?start=site

    Arguments:
        username:
            The username of bot.
        link_type:
            The link type.
        payload:
            The payload of deep link. If it is not a :obj:`str`, it will be converted to a string.

    .. versionadded:: 2.5.0
    .. versionchanged:: 3.0

        * The ``bot_username`` parameter has been changed to :paramref:`username`, and it is now possible to pass a bot object to this parameter in addition to a string.

        * New parameter :paramref:`link_type`
    """
    if not isinstance(username, str):
        from bale import Bot

        if not isinstance(username, Bot):
            raise TypeError("username param must be type of str or Bot")

        u = username.user
        if not u:
            raise RuntimeError(
                "Cannot create start link: Bot user data is not initialized. "
                "Make sure the bot has completed its login/initialization (e.g., `get_me()`) before generating deep links."
            )

        if not u.username:
            raise RuntimeError(
                "Cannot create start link: The bot does not have a username configured. (get_me())"
            )

        username = u.username

    if not (len(username) >= 4 and username.lower().endswith("bot")):
        raise TypeError("username param must be valid bot username.")

    if not re.match(r"^[A-Za-z0-9_-]+$", payload):
        raise TypeError("payload param must be valid payload.")

    url = f"{BALE_BASE_URL}/{username}?{link_type}={payload}"
    return url
