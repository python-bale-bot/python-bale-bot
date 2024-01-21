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
from .file import BaseFile
from typing import Optional

__all__ = (
    "PhotoSize",
)

class PhotoSize(BaseFile):
    """This object represents one size of a photo or a file/sticker thumbnail.

    Attributes
    ----------
        file_id: str
            Identifier for this photo file, which can be used to download or reuse the file.
        file_unique_id: str
            Unique file identifier of thumbnail file.
        width: int
            photo width.
        height: str
            photo height.
        file_size: Optional[:class:`int`]
            photo file size in bytes.
    """
    __slots__ = (
        "file_id",
        "file_unique_id",
        "width",
        "height",
        "file_size"
    )
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int, file_size: Optional[int]):
        super().__init__(file_id, file_unique_id, file_size, width=width, height=height)
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.file_size = file_size

        self._lock()
