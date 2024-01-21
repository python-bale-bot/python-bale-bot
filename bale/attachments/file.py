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
from bale import BaleObject
from typing import Optional, Any
from io import BufferedIOBase

from .input_file import InputFile

__all__ = (
    "BaseFile",
)

class BaseFile(BaleObject):
    """This object shows a Base File Class.

    Attributes
    ----------
        file_id: :class:`str`
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id: :class:`str`
            Unique identifier for this file, which is supposed to be the same over time and for different bots. Can’t be used to download or reuse the file.
        file_size: Optional[:class:`int`]
            File size in bytes, if known.

    .. note::
        You can get more information from the file with ``BaseFile.kwargs_data``.

    """
    __slots__ = (
        "file_id",
        "file_unique_id",
        "file_size",
        "kwargs_data"
    )
    def __init__(self, file_id: str, file_unique_id: str, file_size: Optional[int], **kwargs):
        super().__init__()
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id

        self.file_size = file_size
        self.kwargs_data = kwargs

    async def get(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.get_bot().get_file(self.file_id)

    async def save_to_memory(self, out: "BufferedIOBase" | Any):
        """Download this file into memory. out needs to be supplied with a :class:`io.BufferedIOBase`, the file contents will be saved to that object using the :meth:`io.BufferedIOBase.write` method.

        Parameters
        ----------
            out: :class:`io.BinaryIO`
                A file-like object. Must be opened for writing in binary mode.

        """
        buf = await self.get()

        out.write(buf)

    def to_dict(self):
        data = dict(file_id=self.file_id)
        if self.file_size is not None:
            data['file_size'] = self.file_size

        for key, value in self.kwargs_data.items():
            if value is not None:
                continue

            data['key'] = value

        return data

    def to_input_file(self) -> InputFile:
        """Converts the file to a standard object for sending/uploading it. This object is require in the file sending methods.

        Returns
        --------
            :class:`bale.InputFile`
                The :class:`bale.InputFile` Object for send.
        """
        return InputFile(self.file_id)

    def __len__(self):
        return self.file_size
