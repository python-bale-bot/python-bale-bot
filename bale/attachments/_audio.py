# An API wrapper for Bale written in Python
# Copyright (c) 2022-2024
# Kian Ahmadian <devs@python-bale-bot.ir>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from typing import Optional
from ._basefile import BaseFile

__all__ = (
    "Audio",
)


class Audio(BaseFile):
    """This object shows an Audio.

    Attributes
    ----------
        file_id: :obj:`str`
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id: :obj:`str`
            Unique identifier for this file, which is supposed to be the same over time and for 
            different bots. Can’t be used to download or reuse the file.
        duration: int
            Duration of the audio in seconds as defined by sender.
        title: :obj:`str`, optional
            Title of the audio as defined by sender or by audio tags.
        file_name: :obj:`str`, optional
            Original audio filename as defined by sender.
        mime_type: :obj:`str`, optional
            MIME type of file as defined by sender.
        file_size: :obj:`int`, optional
            File size in bytes, if known.
    """
    __slots__ = (
        "duration",
        "title",
        "file_name",
        "mime_type"
    )

    def __init__(self, file_id: str, file_unique_id: str, duration: int,
                 file_name: Optional[str] = None, title: Optional[str] = None,
                 mime_type: Optional[str] = None, file_size: Optional[int] = None) -> None:
        super().__init__(file_id, file_unique_id, file_size)

        self.duration = duration
        self.file_name = file_name
        self.title = title
        self.mime_type = mime_type

        self._lock()
