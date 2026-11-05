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

from typing import TypeAlias

from .._baleobject import BaleObject
from .._utils.files import parse_file_input
from .._utils.typehint import FileInput
from ._animation import Animation
from ._audio import Audio
from ._basefile import BaseFile
from ._document import Document
from ._inputfile import InputFile
from ._photosize import PhotoSize
from ._video import Video

__all__ = (
    "InputMedia",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "MediaInput",
)

AttachmentType = Audio | Document | PhotoSize | Video | Animation


class InputMedia(BaleObject):
    """ """

    __slots__ = ("type", "media", "caption")

    def __init__(
        self,
        media_type: str,
        media: FileInput | InputFile | AttachmentType,
        caption: str | None = None,
    ) -> None:
        super().__init__()
        self.type = media_type
        self.media = media
        self.caption = caption

        self._lock()


class InputMediaPhoto(InputMedia):
    def __init__(
        self,
        media: FileInput | PhotoSize,
        caption: str | None = None,
        file_name: str | None = None,
    ) -> None:
        media = parse_file_input(media, PhotoSize, filename=file_name)
        super().__init__(BaseFile.PHOTO, media, caption)


class InputMediaVideo(InputMedia):
    def __init__(
        self,
        media: FileInput | Video,
        caption: str | None = None,
        file_name: str | None = None,
    ) -> None:
        media = parse_file_input(media, Video, filename=file_name)
        super().__init__(BaseFile.VIDEO, media, caption)


class InputMediaAnimation(InputMedia):
    def __init__(
        self,
        media: FileInput | Animation,
        caption: str | None = None,
        file_name: str | None = None,
    ) -> None:
        media = parse_file_input(media, Animation, filename=file_name)
        super().__init__(BaseFile.ANIMATION, media, caption)


class InputMediaAudio(InputMedia):
    def __init__(
        self,
        media: FileInput | Audio,
        caption: str | None = None,
        file_name: str | None = None,
    ) -> None:
        media = parse_file_input(media, Audio, filename=file_name)
        super().__init__(BaseFile.AUDIO, media, caption)


class InputMediaDocument(InputMedia):
    def __init__(
        self,
        media: FileInput | Document,
        caption: str | None = None,
        file_name: str | None = None,
    ) -> None:
        media = parse_file_input(media, Document, filename=file_name)
        super().__init__(BaseFile.DOCUMENT, media, caption)


MediaInput: TypeAlias = (
    InputMediaPhoto
    | InputMediaVideo
    | InputMediaAnimation
    | InputMediaAudio
    | InputMediaDocument
)
