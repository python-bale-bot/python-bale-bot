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
from typing import Dict, Optional
from .basefile import BaseFile

__all__ = (
	"Voice",
)

class Voice(BaseFile):
	"""This object shows a Voice.

    Attributes
    ----------
        file_id: :class:`str`
            Identifier for this file, which can be used to download or reuse the file.
        file_unique_id: :class:`str`
            Unique identifier for this file, which is supposed to be the same over time and for different bots. Can’t be used to download or reuse the file.
        file_name: Optional[:class:`str`]
            Original voice filename as defined by sender.
        mime_type: Optional[:class:`str`]
            MIME type of file as defined by sender.
        file_size: Optional[:class:`int`]
            File size in bytes, if known.
    """
	def __init__(self, file_id: str, file_unique_id: str, file_name: Optional[str], mime_type: Optional[str], file_size: Optional[int]):
		super().__init__(file_id, file_unique_id, file_size)
		self.file_name = file_name
		self.mime_type = mime_type
		self.file_size = file_size

		self._lock()

	@classmethod
	def from_dict(cls, data: Optional[Dict], bot):
		data = BaseFile.parse_data(data)
		if not data:
			return None

		return super().from_dict(data, bot)
