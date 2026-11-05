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

from ._basefile import BaseFile

__all__ = ("PhotoSize",)


class PhotoSize(BaseFile):
    """This object represents one size of a photo or a file/sticker thumbnail.

    Attributes:
        file_id (:obj:`str`):
            Identifier for this photo file, which can be used to download or reuse the file.
        file_unique_id (:obj:`str`):
            Unique file identifier of thumbnail file.
        width (:obj:`int`):
            photo width.
        height (:obj:`int`):
            photo height.
        file_size (:obj:`int`, optional):
            photo file size in bytes.
    """

    __slots__ = ("width", "height")

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        file_size: int | None = None,
    ) -> None:
        super().__init__(file_id, file_unique_id, file_size, width=width, height=height)
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.file_size = file_size
