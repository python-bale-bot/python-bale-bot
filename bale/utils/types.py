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