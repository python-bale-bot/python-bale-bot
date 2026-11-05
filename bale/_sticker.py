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
from typing import TYPE_CHECKING

from ._baleobject import BaleObject
from .attachments import PhotoSize

if TYPE_CHECKING:
    pass

__all__ = ("Sticker",)


class Sticker(BaleObject):
    """This object represents a sticker in Bale.

    Attributes:
        file_id (:obj:`str`):
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id (:obj:`str`):
            Unique identifier for this file.
        type (:obj:`str`):
            Type of the sticker, currently can be one of ``regular`` or ``mask``.
        width (:obj:`int`):
            Sticker width.
        height (:obj:`str`):
            Sticker height.
        thumb (:class:`~bale.PhotoSize`, optional):
            Sticker thumbnail
        set_name (:obj:`str`, optional):
            Name of the sticker set to which the sticker belongs.
        file_size (:obj:`int`, optional):
            File size in bytes.
    """

    __slots__ = (
        "file_id",
        "file_unique_id",
        "type",
        "width",
        "height",
        "thumb",
        "set_name",
        "file_size",
    )

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        sticker_type: str,
        width: int,
        height: int,
        thumb: "PhotoSize | None" = None,
        set_name: str | None = None,
        file_size: int | None = None,
    ) -> None:
        super().__init__()
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.type = sticker_type
        self.width = width
        self.height = height
        self.thumb = thumb
        self.set_name = set_name
        self.file_size = file_size

        self._lock()

    async def get_file(self) -> bytes:
        """|shortcut|

        .. code-block:: python

            bytes_sticker = await sticker.get_file("FILE_ID")

        """
        return await self.get_bot().download_file(self.file_id)
