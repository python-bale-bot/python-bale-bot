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
from typing import Optional, Dict
from bale import BaleObject, PhotoSize
from bale.utils.types import MissingValue

__all__ = (
    "Sticker",
)

class Sticker(BaleObject):
    """This object shows a Sticker.

    Attributes
    ----------
        file_id: :obj:`str`
            Identifier for this sticker file, which can be used to download or reuse the file.
        file_unique_id: :obj:`str`
            Unique file identifier of sticker.
        type: :obj:`str`
            Type of the sticker. Currently one of regular and mask.
        width: :obj:`int`
            Sticker width.
        height: :obj:`str`
            Sticker height.
        thumb: :class:`bale.PhotoSize`, optional
            Sticker thumbnail.
        set_name: :obj:`str`, optional
            Name of the sticker set to which the sticker belongs.
        file_size: :obj:`int`, optional
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
    def __init__(self, file_id: str, file_unique_id: str, sticker_type: str, width: int, height: int, thumb: Optional["PhotoSize"] = MissingValue,
                 set_name: Optional[str] = MissingValue, file_size: Optional[int] = MissingValue) -> None:
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

    async def get_file(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.get_bot().get_file(self.file_id)

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot):
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["sticker_type"] = data.pop("type")

        return super().from_dict(data, bot)
