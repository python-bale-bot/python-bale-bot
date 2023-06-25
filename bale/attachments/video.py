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


class Video(File):
    __FILE_TYPE__ = "VIDEO"
    """This object shows a Video.

    Attributes
    ----------
        file_id: str
            Identifier for this file, which can be used to download or reuse the file.
        width: int
            Video width as defined by sender.
        file_size: int
            File size in bytes.
        height: str
            Video height as defined by sender.
        duration: int
            Duration of the video in seconds as defined by sender.
        mime_type: :class:`str`
           MIME type of a file as defined by sender.

    """
    __slots__ = File.__slots__ + (
        "width",
        "height",
        "duration"
    )

    def __init__(self, file_id: str, mime_type: str, width: int, height: int, file_size: int, duration: int, bot: "Bot"):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, duration = duration, width = width, height = height)

        self.width = width
        self.height = height
        self.duration = duration

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot"):
        return cls(
            file_id=data.get("file_id"),
            width=data.get("width"),
            height=data.get("height"),
            file_size=data.get("file_size"),
            duration=data.get("duration"),
            mime_type=data.get("mime_type"),
            bot=bot
        )

