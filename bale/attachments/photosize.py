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
from bale import BaleObject
from typing import Optional

__all__ = (
    "PhotoSize",
)

class PhotoSize(BaleObject):
    """This object represents one size of a photo or a file/sticker thumbnail.

    Attributes
    ----------
        file_id: str
            Identifier for this photo file, which can be used to download or reuse the file.
        file_unique_id: str
            Unique file identifier of thumbnail file.
        width: int
            photo width.
        height: str
            photo height.
        file_size: Optional[:class:`int`]
            photo file size in bytes.
    """
    __slots__ = (
        "file_id",
        "file_unique_id",
        "width",
        "height",
        "file_size"
    )
    def __init__(self, file_id: str, file_unique_id: str, width: int, height: int, file_size: Optional[int]):
        super().__init__()
        self._id = file_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.file_size = file_size

        self._lock()
