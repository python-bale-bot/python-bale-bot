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
from typing import TYPE_CHECKING

from .file import File
if TYPE_CHECKING:
    from bale import Bot


class Photo(File):
    __FILE_TYPE__ = "PHOTO"
    """This object shows a Photo.

    Attributes
    ----------
        file_id: str
            Audio ID
        width: int
            Photo width
        file_size: int
            Audio Size.
        height: str
            Photo height.
    """
    __slots__ = File.__slots__ + (
        "width",
        "height"
    )
    def __init__(self, file_id: str, width: int, height: int, file_size: int, bot: "Bot"):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, "jpg", bot, width = width, height = height)

        self.width = width
        self.height = height

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        return cls(
            file_id=data.get("file_id"),
            width=data.get("width"),
            height=data.get("height"),
            file_size=data.get("file_size"),
            bot=bot
        )
