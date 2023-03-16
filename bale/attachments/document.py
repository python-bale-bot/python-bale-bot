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

if TYPE_CHECKING:
	from bale import Bot


class Document:
	"""This object shows a Document.

    Attributes
    ----------
        file_id: Optional[:class:`str`]
        file_name: Optional[:class:`str`]
        mime_type: Optional[:class:`str`]
        file_size: Optional[:class:`int`]
    """
	__slots__ = (
		"file_id",
		"file_name",
		"mime_type",
		"file_size",
		"bot"
	)

	def __init__(self, file_id: str = None, file_name: str = None, mime_type: str = None, file_size: int = None,
	             bot: "Bot" = None):
		self.file_id = file_id if file_id is not None else None
		self.file_name = file_name if file_name is not None else None
		self.mime_type = mime_type if mime_type is not None else None
		self.file_size = file_size if file_size is not None else None
		self.bot = bot

	async def read(self):
		"""Read the Document.

        Returns
        -------
            :class:`bytes`
                Document
        Raises
        ------
            NotFound
                Document not found.
            Forbidden
                You do not have permission to read document.
            APIError
                Read document Failed.

        """
		return await self.bot.http.get_file(self.file_id)

	async def save(self, file_name):
		"""Save the Document.

        Parameters
        ----------
            file_name: str

        Raises
        ------
            NotFound
                Document not found.
            Forbidden
                You do not have permission to read document.
            APIError
                Read document Failed.
            OSError
                Open or write into file Failed.
        """
		data = await self.read()
		with open(file_name, 'wb') as file:
			return file.write(data)

	@classmethod
	def from_dict(cls, data: dict, bot: "Bot" = None):
		return cls(file_id=data.get("file_id"), file_name=data.get("file_name"),
		           mime_type=data.get("mime_type"), file_size=data.get("file_size"), bot=bot)

	def to_dict(self):
		data = { "file_id": self.file_id, "file_name": self.file_name, "mime_type": self.mime_type,
		         "file_size": self.file_size }

		return data
