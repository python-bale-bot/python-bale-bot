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
from typing import Union, Dict, Any, TypeVar, Callable, Coroutine, TYPE_CHECKING
from pathlib import Path
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

class _MissingValue:
    __slots__ = ()

    def reject_function(self):
        return False

    def __str__(self):
        return None

    def __repr__(self):
        return "Default None Value"

    def __hash__(self):
        return 0

    __eq__ = __ne__ = __le__ = __ge__ = __lt__ = __gt__ = reject_function

MissingValue: Any = _MissingValue()
