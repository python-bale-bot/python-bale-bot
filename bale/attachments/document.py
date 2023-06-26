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


class Document(File):
	"""This object shows a Document.

    Attributes
    ----------
        file_id: :class:`str`
        	Identifier for this file, which can be used to download or reuse the file.
        file_name: Optional[:class:`str`]
        	Original filename as defined by sender.
        mime_type: Optional[:class:`str`]
        	MIME type of the file as defined by sender.
        file_size: Optional[:class:`int`]
        	File size in bytes.
    """
	__FILE_TYPE__ = "DOCUMENT"
	__slots__ = File.__slots__ + (
		"file_name",
	)

	def __init__(self, file_id: str, file_name: str = None, mime_type: str = None, file_size: int = None,
	             bot: "Bot" = None):
		super().__init__(self.__FILE_TYPE__, file_id, file_size, mime_type, bot, file_name=file_name)
		self.file_name = file_name if file_name is not None else None

	@classmethod
	def from_dict(cls, data: dict, bot: "Bot" = None):
		return cls(file_id=data.get("file_id"), file_name=data.get("file_name"),
		           mime_type=data.get("mime_type"), file_size=data.get("file_size"), bot=bot)
