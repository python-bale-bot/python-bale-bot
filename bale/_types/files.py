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

import sys
from typing import TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

__all__ = ("PhotoSize", "Animation", "Audio", "Document", "Video", "Voice")


class PhotoSize(TypedDict, total=False):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: NotRequired[int | None]


class Animation(TypedDict, total=False):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: PhotoSize | None
    file_name: NotRequired[str | None]
    mime_type: NotRequired[str | None]
    file_size: NotRequired[int | None]


class Audio(TypedDict, total=False):
    file_id: str
    file_unique_id: str
    duration: int
    title: NotRequired[str | None]
    file_name: NotRequired[str | None]
    mime_type: NotRequired[str | None]
    file_size: NotRequired[int | None]


class Document(TypedDict, total=False):
    file_id: str
    file_unique_id: str
    thumbnail: PhotoSize | None
    file_name: NotRequired[str | None]
    mime_type: NotRequired[str | None]
    file_size: NotRequired[int | None]


class Video(TypedDict, total=False):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    file_name: NotRequired[str | None]
    mime_type: NotRequired[str | None]
    file_size: NotRequired[int | None]


class Voice(TypedDict, total=False):
    file_id: str
    file_unique_id: str
