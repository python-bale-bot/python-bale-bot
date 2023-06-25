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


class Audio(File):
    __FILE_TYPE__ = "AUDIO"
    """This object shows a Audio.

    Attributes
    ----------
        file_id: str
            Identifier for this file, which can be used to download or reuse the file.
        duration: int
            Duration of the audio in seconds as defined by sender.
        file_size: int
            File size in bytes.
        mime_type: Optional[:class:`str`]
            MIME type of the file as defined by sender.
        title: Optional[:class:`str`]
            Title of the audio as defined by sender or by audio tags.
    """
    __slots__ = File.__slots__ + (
        "duration",
        "title"
    )

    def __init__(self, file_id: str, duration: int = None, file_size: int = None, bot: "Bot" = None, mime_type: str = None, title: str = None):
        super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, duration=duration, title=title)

        self.duration = duration
        self.title = title

    @classmethod
    def from_dict(cls, data, bot: "Bot"):
        return cls(file_id=data["file_id"], duration=data["duration"], file_size=data["file_size"], title=data["title"],
                   mime_type=data["mime_type"], bot=bot)