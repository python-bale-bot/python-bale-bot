#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

from typing import TYPE_CHECKING

from ._basefile import BaseFile
from ._photosize import PhotoSize

if TYPE_CHECKING:
    from .._types.files import Document as DocumentPayload

__all__ = ("Document",)


class Document(BaseFile):
    """This object shows a Document.

    Attributes:
        file_id (:obj:`str`):
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id (:obj:`str`):
            Unique identifier for this file, which is supposed to be the same over time and for
            different bots. Can’t be used to download or reuse the file.
        thumbnail (:class:`~bale.PhotoSize`, optional):
            document thumbnail as defined by sender.
        file_name (:obj:`str`, optional):
            Original document filename as defined by sender.
        mime_type (:obj:`str`, optional):
            MIME type of file as defined by sender.
        file_size (:obj:`int`, optional):
            File size in bytes, if known.
    """

    __slots__ = ("thumbnail", "file_name", "mime_type")

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        file_name: str | None = None,
        thumbnail: "PhotoSize | None" = None,
        mime_type: str | None = None,
        file_size: int | None = None,
    ) -> None:
        super().__init__(file_id, file_unique_id, file_size)
        self.thumbnail = thumbnail
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size

        self._lock()

    @classmethod
    def from_dict(cls, data: "DocumentPayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaseFile.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["thumbnail"] = PhotoSize.from_dict(
            parsed_data.get("thumbnail"), bot
        )

        return super().from_dict(parsed_data, bot)
