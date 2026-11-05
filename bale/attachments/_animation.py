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

from typing import TYPE_CHECKING

from ._basefile import BaseFile
from ._photosize import PhotoSize

if TYPE_CHECKING:
    from .._types.files import Animation as AnimationPayload

__all__ = ("Animation",)


class Animation(BaseFile):
    """This object shows an Animation.

    Attributes:
        file_id (:obj:`str`):
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id (:obj:`str`):
            Unique identifier for this file, which is supposed to be the same over time and for
            different bots. Can’t be used to download or reuse the file.
        width (:obj:`int`):
            Animation width as defined by sender.
        height (:obj:`int`):
            Animation height as defined by sender.
        duration (:obj:`int`):
            Duration of the animation in seconds as defined by sender.
        thumbnail (:class:`~bale.PhotoSize`, optional):
            Animation thumbnail as defined by sender.
        file_name (:obj:`str`, optional):
            Original animation filename as defined by sender.
        mime_type (:obj:`str`, optional):
            MIME type of file as defined by sender.
        file_size (:obj:`int`, optional):
            File size in bytes, if known.
    """

    __slots__ = ("width", "height", "duration", "thumbnail", "file_name", "mime_type")

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        file_name: str | None = None,
        thumbnail: "PhotoSize | None" = None,
        mime_type: str | None = None,
        file_size: int | None = None,
    ) -> None:
        super().__init__(file_id, file_unique_id, file_size)

        self.width = width
        self.height = height
        self.duration = duration
        self.file_name = file_name
        self.thumbnail = thumbnail
        self.mime_type = mime_type

        self._lock()

    @classmethod
    def from_dict(cls, data: "AnimationPayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaseFile.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["thumbnail"] = PhotoSize.from_dict(
            parsed_data.get("thumbnail"), bot
        )

        return super().from_dict(parsed_data, bot)
