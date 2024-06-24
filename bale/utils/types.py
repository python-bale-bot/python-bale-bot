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
from pathlib import Path
from typing import Union, Dict, Any, TypeVar, Callable, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from bale import (
        Audio,
        Document,
        PhotoSize,
        Video,
        Animation,
        Voice,
        InputMedia,
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

    def __le__(self, _):
        return False

    def __ge__(self, _):
        return False

    def __lt__(self, _):
        return False

    def __gt__(self, _):
        return False

    def __hash__(self):
        return 0

    def __bool__(self):
        return False


MissingValue: MissingValueType = MissingValueType()

class _MaybeMissingGenerator:
    __slots__ = ()

    def __getitem__(self, item: Union[tuple, Any]) -> Union[MissingValue, ...]:
        if not isinstance(item, tuple):
            item = (item, )
        return Union[(MissingValueType, ) + item]

OptionalParam = _MaybeMissingGenerator()
