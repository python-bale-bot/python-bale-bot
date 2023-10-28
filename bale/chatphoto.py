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
from typing import Optional, Dict, Self, TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "ChatPhoto",
)

class ChatPhoto:
    """
    This object represents a chat photo.

    Attributes
    ----------
        small_file_id: Optional[:class:`str`]
            File identifier of small (160 x 160) chat photo.
        small_file_unique_id: Optional[:class:`str`]
            Unique file identifier of small (160 x 160) chat photo.
        big_file_id: Optional[:class:`str`]
            File identifier of big (640 x 640) chat photo.
        big_file_unique_id: Optional[:class:`str`]
            Unique file identifier of big (640 x 640) chat photo.
    """
    __slots__ = (
        "small_file_id",
        "small_file_unique_id",
        "big_file_id",
        "big_file_unique_id"
    )
    def __init__(self, small_file_id: Optional[str] = None, small_file_unique_id: Optional[str] = None, big_file_id: Optional[str] = None, big_file_unique_id: Optional[str] = None):
        self.small_file_id = small_file_unique_id
        self.small_file_unique_id = small_file_unique_id
        self.big_file_id = big_file_unique_id
        self.big_file_unique_id = big_file_unique_id

    @classmethod
    def from_dict(cls, data : Dict) -> Self:
        return cls(data.get('small_file_id'), data.get('small_file_unique_id'), data.get('big_file_id'), data.get('big_file_unique_id'))
