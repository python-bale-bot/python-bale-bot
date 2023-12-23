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
from typing import Optional, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "Sticker",
)

class Sticker:
    """This object shows a Sticker.

    Attributes
    ----------
        file_id: str
            Identifier for this sticker file, which can be used to download or reuse the file.
        file_unique_id: str
            Unique file identifier of sticker.
        type: str
            Type of the sticker. Currently one of regular and mask.
        width: int
            Sticker width.
        height: str
            Sticker height.
        file_size: int
            File size in bytes.
    """
    __slots__ = (
        "file_id",
        "file_unique_id",
        "type",
        "width",
        "height",
        "file_size",
        "bot"
    )
    def __init__(self, file_id: str, file_unique_id: str, type: str, width: int, height: int, bot: "Bot", file_size: Optional[int] = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.type = type
        self.width = width
        self.height = height
        self.file_size = file_size
        self.bot = bot

    async def get_file(self) -> bytes:
        """
        For the documentation of the arguments, please see :meth:`bale.Bot.get_file`.
        """
        return await self.bot.get_file(self.file_id)

    @classmethod
    def from_dict(cls, data: Dict, bot: "Bot") -> "Sticker":
        return cls(
            file_id=data.get('file_id'), file_unique_id=data.get('file_unique_id'), type=data.get('type'),
            width=data.get('width'), height=data.get('height'), file_size=data.get('file_size'), bot=bot
        )
