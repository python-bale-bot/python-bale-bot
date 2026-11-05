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
from ._baleobject import BaleObject

__all__ = ("PollOption",)


class PollOption(BaleObject):
    """This object represents a poll option.

    Attributes:
        persistent_id (:obj:`str`):
            Unique identifier of the option, persistent on option addition and deletion.
        text (:obj:`str`):
            Option text, ``1``-``100`` characters.
        voter_count (:obj:`int`):
            Number of users who voted for this option.

    .. versionadded:: 3.0
    """

    __slots__ = ("persistent_id", "text", "voter_count")

    def __init__(self, persistent_id: str, text: str, voter_count: int) -> None:
        super().__init__()
        self.persistent_id = persistent_id
        self.text = text
        self.voter_count = voter_count

        self._lock()
