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

from typing import Optional, Union
from bale import BaleObject
from ._inputfile import InputFile
from ._basefile import BaseFile
from ._photosize import PhotoSize
from ._document import Document
from ._audio import Audio
from ._video import Video
from ._animation import Animation

from bale.utils.files import parse_file_input
from bale.utils.types import AttachmentType, FileInput

__all__ = (
    "InputMedia",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument"
)

class InputMedia(BaleObject):
    __slots__ = (
        "type",
        "media",
        "caption"
    )
    def __init__(self, media_type: str, media: Union[FileInput, InputFile, AttachmentType], caption: Optional[str] = None) -> None:
        super().__init__()
        self.type = media_type
        self.media = media
        self.caption = caption

        self._lock()


class InputMediaPhoto(InputMedia):
    def __init__(self, media: Union[FileInput, PhotoSize], caption: Optional[str] = None, file_name: Optional[str] = None) -> None:
        media = parse_file_input(media, PhotoSize, file_name=file_name)
        super().__init__(BaseFile.PHOTO, media, caption)

class InputMediaVideo(InputMedia):
    def __init__(self, media: Union[FileInput, Video], caption: Optional[str] = None, file_name: Optional[str] = None) -> None:
        media = parse_file_input(media, Video, file_name=file_name)
        super().__init__(BaseFile.VIDEO, media, caption)

class InputMediaAnimation(InputMedia):
    def __init__(self, media: Union[FileInput, Animation], caption: Optional[str] = None, file_name: Optional[str] = None) -> None:
        media = parse_file_input(media, Animation, file_name=file_name)
        super().__init__(BaseFile.ANIMATION, media, caption)

class InputMediaAudio(InputMedia):
    def __init__(self, media: Union[FileInput, Audio], caption: Optional[str] = None, file_name: Optional[str] = None) -> None:
        media = parse_file_input(media, Audio, file_name=file_name)
        super().__init__(BaseFile.AUDIO, media, caption)

class InputMediaDocument(InputMedia):
    def __init__(self, media: Union[FileInput, Document], caption: Optional[str] = None, file_name: Optional[str] = None) -> None:
        media = parse_file_input(media, Document, file_name=file_name)
        super().__init__(BaseFile.DOCUMENT, media, caption)
