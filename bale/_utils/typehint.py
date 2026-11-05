# An API wrapper for Bale written in Python
# Copyright (c) 2022-2026
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

if TYPE_CHECKING:
    from bale import InputFile  # noqa
    from bale import (InputMediaAnimation, InputMediaAudio, InputMediaDocument,
                      InputMediaPhoto, InputMediaVideo)


class _Sentinel(Enum):
    MISSING = object()
    """
    Hint:

         Usage example:

         .. code-block:: python

             def process_value(value: SentinelOrValue[int] = MISSING):
                 if MISSING.is_default(value):
                     print("This parameter has not been used.")
                 elif value is None:
                     print("The parameter has been used, and the user has passed None explicitly.")
                 else:
                     print(f"The value is an integer: {value}")
    """

    __slots__ = ()

    def __bool__(self):
        return False

    def __repr__(self):
        return "Sentinel"

    @staticmethod
    def is_default(value: Any) -> bool:
        """Check if the given value is ``MISSING``."""
        return value is _Sentinel.MISSING


T = TypeVar("T")
Coro = Coroutine[Any, Any, T]
CoroFunc = Callable[..., Coro[Any]]
CoroT = TypeVar("CoroT", bound=CoroFunc)
MaybeCoro = T | Coro[T]
MaybeFunc = T | Callable[..., T]
MaybeCoroFunc = T | CoroFunc
MaybeAwaitable = T | Awaitable[T]
MISSING = _Sentinel.MISSING
SentinelOrValue: TypeAlias = T | _Sentinel | None

JSONDICT = dict[str, Any]
_Button = "InlineKeyboardButton | KeyboardButton"
PayloadType = dict[str, Any] | None


FileInput: TypeAlias = "str | bytes | Path | InputFile"

MediaInput: TypeAlias = (
    "InputMediaPhoto | InputMediaVideo | InputMediaAnimation | InputMediaAudio | InputMediaDocument"  # noqa
)
