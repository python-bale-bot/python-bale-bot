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
from typing import Optional, TYPE_CHECKING
from bale import BaleObject
if TYPE_CHECKING:
    from bale import BaseFile

__all__ = (
    "ChatPhoto",
)

class ChatPhoto(BaleObject):
    """This object represents a chat photo.

    Attributes
    ----------
        small_file_id: Optional[:class:`str`]
            File identifier of small (160 x 160) chat photo.
        small_file_unique_id: Optional[:class:`str`]
            Unique file identifier of small (160 x 160) chat photo.
        big_file_id: Optional[:class:`str`]
            File identifier of big (640 x 640) chat photo.
        big_file_unique_id: Optional[:class:`str`]
            Unique file identifier of big (640 x 640) chat photo.
    """
    __slots__ = (
        "small_file_id",
        "small_file_unique_id",
        "big_file_id",
        "big_file_unique_id"
    )
    def __init__(self, small_file_id: Optional[str] = None, small_file_unique_id: Optional[str] = None,
                 big_file_id: Optional[str] = None, big_file_unique_id: Optional[str] = None):
        super().__init__()
        self.small_file_id = small_file_unique_id
        self.small_file_unique_id = small_file_unique_id
        self.big_file_id = big_file_unique_id
        self.big_file_unique_id = big_file_unique_id
        self._lock()

    @property
    def small_file_object(self) -> "BaseFile":
        """Optional[:class:`bale.BaseFile`]: Represents the small file object."""
        from bale import BaseFile
        obj = BaseFile(self.small_file_id, self.small_file_unique_id, None)
        obj.set_bot(self.bot)
        return obj

    @property
    def big_file_object(self) -> "BaseFile":
        """Optional[:class:`bale.BaseFile`]: Represents the big file object."""
        from bale import BaseFile
        obj = BaseFile(self.big_file_id, self.big_file_unique_id, None)
        obj.set_bot(self.bot)
        return obj