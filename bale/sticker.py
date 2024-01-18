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
from typing import Optional
from bale import BaleObject, PhotoSize

__all__ = (
    "Sticker",
)

class Sticker(BaleObject):
    """This object shows a Sticker.

    Attributes
    ----------
        file_id: str
            Identifier for this sticker file, which can be used to download or reuse the file.
        file_unique_id: str
            Unique file identifier of sticker.
        type: str
            Type of the sticker. Currently one of regular and mask.
        width: int
            Sticker width.
        height: str
            Sticker height.
        thumb: Optional[:class:`bale.PhotoSize`]
            Sticker thumbnail.
        set_name: Optional[:class:`str`]
            Name of the sticker set to which the sticker belongs.
        file_size: Optional[:class:`int`]
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
        "file_size"
    )
    def __init__(self, file_id: str, file_unique_id: str, type: str, width: int, height: int, thumb: Optional["PhotoSize"], set_name: Optional[str] = None, file_size: Optional[int] = None):
        super().__init__()
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.type = type
        self.width = width
        self.height = height
        self.thumb = thumb
        self.set_name = set_name
        self.file_size = file_size

    async def get_file(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.get_bot().get_file(self.file_id)
