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

from io import BufferedIOBase
from typing import Any, ClassVar

from .._baleobject import BaleObject

__all__ = ("BaseFile",)


class BaseFile(BaleObject):
    """This object shows a Base File Class.

    Attributes:
        file_id (:obj:`str`):
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id (:obj:`str`):
            Unique identifier for this file, which is supposed to be the same over time and for
            different bots. Can’t be used to download or reuse the file.
        file_size (:obj:`int`, optional):
            File size in bytes, if known.

    Note:
        You can get more information from the file with ``BaseFile.kwargs_data``.

    """

    __slots__ = ("file_id", "file_unique_id", "file_size", "kwargs_data")
    PHOTO: ClassVar[str] = "photo"
    VIDEO: ClassVar[str] = "video"
    DOCUMENT: ClassVar[str] = "document"
    AUDIO: ClassVar[str] = "audio"
    ANIMATION: ClassVar[str] = "animation"

    def __init__(
        self, file_id: str, file_unique_id: str, file_size: int | None = None, **kwargs
    ) -> None:
        super().__init__()
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id

        self.file_size = file_size
        self.kwargs_data = kwargs

    async def get(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`~bale.Bot.download_file`.
        """
        return await self.get_bot().download_file(self.file_id)

    async def save_to_memory(
        self, out: "BufferedIOBase | Any", close_file: bool = False
    ) -> None:
        """Download this file into memory. out needs to be supplied with a :class:`io.BufferedIOBase`,
        the file contents will be saved to that object using the :meth:`io.BufferedIOBase.write` method.

        Arguments:
            out:
                A file-like object. Must be opened for writing in binary mode.
            close_file:
                If :obj:`True`, the file will be closed after writing. Default is :obj:`False`.

        """
        buf = await self.get()

        out.write(buf)
        if close_file:
            out.close()

    def to_dict(self) -> dict:
        data: dict[str, Any] = {"file_id": self.file_id}
        if self.file_size is not None:
            data["file_size"] = self.file_size

        for key, value in self.kwargs_data.items():
            if value is None:
                continue

            data[key] = value

        return data

    def __len__(self):
        return self.file_size
