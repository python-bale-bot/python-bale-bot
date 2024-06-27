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
from typing import Optional
from bale import BaleObject

__all__ = (
    "ChatPhoto",
)


class ChatPhoto(BaleObject):
    """This object represents a chat photo.

    Attributes
    ----------
        small_file_id: :obj:`str`, optional
            File identifier of small (160 x 160) chat photo.
        small_file_unique_id: :obj:`str`, optional
            Unique file identifier of small (160 x 160) chat photo.
        big_file_id: :obj:`str`, optional
            File identifier of big (640 x 640) chat photo.
        big_file_unique_id: :obj:`str`, optional
            Unique file identifier of big (640 x 640) chat photo.
    """
    __slots__ = (
        "small_file_id",
        "small_file_unique_id",
        "big_file_id",
        "big_file_unique_id"
    )
    def __init__(self, small_file_id: Optional[str] = MissingValue, small_file_unique_id: Optional[str] = MissingValue,
                 big_file_id: Optional[str] = MissingValue, big_file_unique_id: Optional[str] = MissingValue) -> None:
        super().__init__()
        self.small_file_id = small_file_id
        self.small_file_unique_id = small_file_unique_id
        self.big_file_id = big_file_id
        self.big_file_unique_id = big_file_unique_id
        self._lock()

    async def get_small_file(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.get_bot().get_file(self.small_file_id)

    async def get_big_file(self):
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.get_bot().get_file(self.big_file_id)
