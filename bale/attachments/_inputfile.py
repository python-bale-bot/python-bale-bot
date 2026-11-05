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

from io import BufferedReader, IOBase
from pathlib import Path
from typing import Any, BinaryIO, Type

from .._utils.files import is_file_valid

__all__ = ("InputFile",)


class InputFile:
    """This object shows a file or bytes ready to upload.

    .. admonition:: Examples

        :any:`examples.attachment`

    .. code-block:: python

        # upload the file
        with open('./my_file.png', 'rb') as f:
            file = InputFile(f.read())

    Arguments:
        data:
            Your file to upload.
        filename:
            Additional interface options.
    """

    __slots__ = ("_data", "_filename")

    def __init__(
        self,
        data: bytes | IOBase | BinaryIO,
        *,
        filename: str | None = None,
    ) -> None:
        if not isinstance(data, (str, BufferedReader, bytes)):
            raise TypeError(
                "file_input parameter must be one of bytes, BufferedReader and BinaryIO types"
            )

        if filename and not isinstance(filename, str):
            raise TypeError("file_name param must be type of str")

        self._data: bytes | IOBase | BinaryIO = data
        self._filename: str | None = filename

    @classmethod
    def from_bytes(
        cls: Type["InputFile"], data: bytes, filename: str | None = None
    ) -> InputFile:
        return InputFile(data, filename=filename)

    @classmethod
    def from_path(
        cls: Type["InputFile"], path: str | Path, filename: str | None = None
    ) -> InputFile:
        if p := is_file_valid(path):
            return InputFile(p.open("rb"), filename=filename or p.name)

        raise FileNotFoundError(f"File not found: {path}")

    def to_multipart_payload(self) -> dict[str, Any]:
        payload = {"value": self._data, "content_type": "multipart/form-data"}
        if self._filename:
            payload["filename"] = self._filename

        return payload

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InputFile) and self._data == other._data

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<InputFile file_name={self._filename}>"
