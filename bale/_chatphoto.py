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

from ._baleobject import BaleObject

__all__ = ("ChatPhoto",)


class ChatPhoto(BaleObject):
    """This object represents a chat photo in the Bale messenger.

    Attributes:
        small_file_id (:obj:`str`, optional):
            File identifier of small (160x160) chat photo.
        small_file_unique_id (:obj:`str`, optional):
            Unique file identifier of small (160x160) chat photo.
        big_file_id (:obj:`str`, optional):
            File identifier of big (640x640) chat photo.
        big_file_unique_id (:obj:`str`, optional):
            Unique file identifier of big (640x640) chat photo.

    .. versionadded:: 3.0
    """

    __slots__ = (
        "small_file_id",
        "small_file_unique_id",
        "big_file_id",
        "big_file_unique_id",
    )

    def __init__(
        self,
        small_file_id: str,
        small_file_unique_id: str,
        big_file_id: str,
        big_file_unique_id: str,
    ) -> None:
        super().__init__()
        self.small_file_id = small_file_id
        self.small_file_unique_id = small_file_unique_id
        self.big_file_id = big_file_id
        self.big_file_unique_id = big_file_unique_id

        self._lock()

    async def download_small_file(self):
        """|shortcut|


        .. versionchanged:: 3.0
            The method renamed from ``get_small_file``.
        """
        return await self.get_bot().download_file(self.small_file_id)

    async def download_big_file(self):
        """|shortcut|


        .. versionchanged:: 3.0
            The method renamed from ``get_big_file``.
        """
        return await self.get_bot().download_file(self.big_file_id)
