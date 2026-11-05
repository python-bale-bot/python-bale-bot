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
from typing import Any

from .._exceptions import InvalidToken

__all__ = ("extract_bot_id", "validate_token")

# simple token: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz


def extract_bot_id(token: str) -> int | None:
    """Extracts the bot ID from a given Bale bot token.

    A Bale bot token follows the format: ``<bot_id>:<key>``, where ``<bot_id>`` is a numeric identifier representing the bot's unique ID.

    .. admonition:: Example Code
        :class: tip

        .. code-block:: python

            bot_id = token.extract_bot_id("123456789:ABCDEF1234567890abcdef")
            print(bot_id)  # Output: 123456789

    Arguments:
        token:
            A valid Bale bot token.

    Returns:
        The extracted bot ID as an integer.

    .. versionadded:: 3.0
    """
    _id, *_ = token.split(":")

    try:
        return int(_id)
    except (ValueError, TypeError):
        return None


def validate_token(token: Any) -> None:
    """Validates whether the given token is a properly formatted Bale bot token.

    A valid Bale bot token follows the format: ``<bot_id>:<api_key>``, where ``<bot_id>`` is a numeric identifier and ``<api_key>`` is an alphanumeric string.

    This function checks:

    - If the token is a string.
    - If the token does not contain spaces or invalid whitespace characters.
    - If the token is in the correct format with a numeric bot ID.

    .. admonition:: Example Code
        :class: tip

        .. code-block:: python

            validate_token("123456789:ABCDEF1234567890abcdef")  # Valid token
            validate_token(123456789)  # Raises InvalidToken
            validate_token("ABCDEF1234567890abcdef:123456789")  # Raises InvalidToken

    Arguments:
        token:
            The token to be validated.

    Raises
    ------
        bale.InvalidToken
            If the token is not a string, contains spaces, or does not follow the correct format.

    .. versionadded:: 3.0
    """
    default_message = "The token is invalid. "
    if not isinstance(token, str):
        raise InvalidToken(default_message + "because token must be a str.")

    if any(ord(c) in (9, 10, 11, 12, 13, 32) for c in token):
        raise InvalidToken(default_message + "because token must not contain spaces.")

    # simple token: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
    bot_id, sep, hashed_token = token.partition(":")
    if not (bot_id and sep and hashed_token) or not bot_id.isdigit():
        raise InvalidToken(
            default_message
            + "because token must follow the format: <bot_id>:<api_key>, where <bot_id> is a numeric identifier and <api_key> is an alphanumeric string."
        )
