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
from pathlib import Path
from typing import Union, Dict, Any, TypeVar, Callable, Coroutine, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from bale import (
        Audio,
        Document,
        PhotoSize,
        Video,
        Animation,
        Voice,
        InputMediaPhoto,
        InputMediaVideo,
        InputMediaAnimation,
        InputMediaAudio,
        InputMediaDocument
    )

STOP_UPDATER_MARKER = object()
JSONDICT = Dict[str, Any]
T = TypeVar('T')
F = TypeVar('F')
UT = TypeVar('UT')
Coro = Coroutine[Any, Any, T]
CoroT = TypeVar('CoroT', bound=Callable[..., Coro[Any]])

FileInput = Union[str, bytes, Path]

AttachmentType = Union[
    "Audio",
    "Document",
    "PhotoSize",
    "Video",
    "Animation",
    "Voice"
]

MediaInput = Union[
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument"
]


class MissingValueType:
    __slots__ = ()

    def __str__(self):
        return "Missing"

    def __repr__(self):
        return "MissingValue"

    def __eq__(self, other):
        return isinstance(other, MissingValueType)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 0

    def __bool__(self):
        return False


MissingValue: MissingValueType = MissingValueType()

G = TypeVar('G')


class _MaybeMissingGenerator:
    """
    A generator class to create type hints for values that may be missing.

    This class allows the creation of type hints that include a special
    `MissingValueType`, indicating a value that is considered missing.
    This can be useful in situations where you need to differentiate between
    a value being `None` and a value being missing.

    Usage example:
        .. code:: python
            from bale.utils.types import MissingValue, MaybeMissing

            def process_value(value: MaybeMissing[int]):
                if value is MissingValue:
                    print("The value is missing.")
                else:
                    print(f"The value is an integer: {value}")

    """
    __slots__ = ()

    def __getitem__(self, item: Union[Tuple[Any, ...], Any]) -> Union[MissingValueType, G]:
        if not isinstance(item, tuple):
            item = (item, )
        items = (MissingValueType,) + item

        return Union[items]


MaybeMissing = _MaybeMissingGenerator()
