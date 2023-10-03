"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, Optional, Any
from io import BufferedIOBase
from .input_file import InputFile

if TYPE_CHECKING:
    from bale import Bot


class File:
    """This object shows a Base File Class.

    Attributes
    ----------
        file_type: :class:`str`
            Type of the file.
        file_id: :class:`str`
            Identifier for this file, which can be used to download or reuse the file.
        file_size: Optional[:class:`int`]
            File size in bytes.
        mime_type: Optional[:class:`str`]
            MIME type of the file as defined by sender.
        extra: Optional[:class:`dict`]
            The rest of the file information.

        .. note::
            You can get more information in file with :param:`extra`

    """
    __slots__ = (
        "file_type",
        "file_id",
        "file_size",
        "mime_type",
        "extra",
        "bot"
    )
    def __init__(self, file_type: str, file_id: str, file_size: Optional[int], mime_type: Optional[str], bot: "Bot", **kwargs):
        self.file_type = file_type
        self.file_id = file_id
        self.file_size = file_size
        self.mime_type = mime_type
        self.extra = kwargs
        self.bot = bot

    @property
    def type(self) -> str:
        """:class:`str`: a Shortcut for use :attr:`bale.File.file_type`"""
        return self.file_type

    @property
    def base_file(self) -> "File":
        """:class:`bale.File`: Represents the Base File Class of this file"""
        return File(self.file_type, self.file_id, self.file_size, self.mime_type, self.bot, **self.extra)

    async def get(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.bot.get_file(self.file_id)

    async def save_to_memory(self, out: "BufferedIOBase" | Any) -> NoReturn:
        """Download this file into memory. out needs to be supplied with a :class:`io.BufferedIOBase`, the file contents will be saved to that object using the :meth:`io.BufferedIOBase.write` method.

        Parameters
        ----------
            out: :class:`io.BinaryIO`
                A file-like object. Must be opened for writing in binary mode.

        """
        buf = await self.get()

        out.write(buf)

    def to_dict(self):
        data = {"file_id": self.file_id, "file_size": self.file_size, "mime_type": self.mime_type,
                **self.extra}

        return data

    def to_input_file(self) -> InputFile:
        return InputFile(self.file_id)

    def __len__(self):
        return self.file_size

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.file_id == other.file_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"<File file_type={self.file_type} file_id={self.file_id} file_size={self.file_size} >"

    def __str__(self):
        return self.file_id
