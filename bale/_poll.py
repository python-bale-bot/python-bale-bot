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
from typing import TYPE_CHECKING, Literal

from ._baleobject import BaleObject
from ._polloption import PollOption

if TYPE_CHECKING:
    from ._types.poll import Poll as PollPayload

__all__ = ("Poll",)


class Poll(BaleObject):
    """This object represents a poll in Bale.

    Equality conditions:
        1. The second object must be an instance of the :class:`Poll` class.
        2. Both must have the same :attr:`id`.

    Attributes:
        id (:obj:`str`):
            Unique poll identifier.
        question (:obj:`str`):
            Poll question, ``1``-``300`` characters.
        options (list of :class:`~bale.PollOption`, optional):
            List of poll options.
        type (:obj:`str`):
            Poll type. Up to this version, Bale only supports the ``REGULAR`` type (standard voting). However, generally, Telegram also supports a ``QUIZ`` type, which includes a correct answer option in addition to the standard fields.
        total_voter_count (:obj:`int`):
            Total number of users who have voted in the poll so far (if active) or in total (if closed).
        is_closed (:obj:`bool`):
            :obj:`True`, if the poll is closed. When a poll is closed, its results become visible to all members, and participants can no longer vote or change their votes.
        is_anonymous (:obj:`bool`):
            :obj:`True`, if the poll is anonymous. This means that no members, including the creator, admins, and regular group/channel members, can see other individuals' votes or participants.
        allows_multiple_answers (:obj:`bool`):
            If this value is `:obj:`True`, multiple options can be selected in the poll.
        allows_revoting (:obj:`bool`):
           :obj:`True`, if the poll allows users to change their selected option(s) after casting them. Note that this is not possible after the poll has ended.
        members_only (:obj:`bool`):
           :obj:`True`, if the poll is restricted only to users whose membership duration in the chat where the poll was initially sent exceeds 24 hours.


    .. versionadded:: 3.0
    """

    __slots__ = (
        "id",
        "question",
        "options",
        "total_voter_count",
        "is_closed",
        "is_anonymous",
        "type",
        "allows_multiple_answers",
        "allows_revoting",
        "members_only",
    )

    def __init__(
        self,
        id: str,
        question: str,
        options: list["PollOption"],
        total_voter_count: int,
        is_closed: bool,
        is_anonymous: bool,
        type: Literal["REGULAR", "QUIZ"],
        allows_multiple_answers: bool,
        allows_revoting: bool,
        members_only: bool,
    ) -> None:
        super().__init__()

        self._id = id
        self.id = id
        self.question = question
        self.options = options
        self.total_voter_count = total_voter_count
        self.is_closed = is_closed
        self.is_anonymous = is_anonymous
        self.type = type
        self.allows_multiple_answers = allows_multiple_answers
        self.allows_revoting = allows_revoting
        self.members_only = members_only

        self._lock()

    @classmethod
    def from_dict(
        cls,
        data: "PollPayload | None" = None,
        bot=None,
    ):
        """:meta private:"""
        data = BaleObject.parse_data(data)
        if data is None:
            return None

        data["options"] = PollOption.from_list(data.get("options"), bot)

        return super().from_dict(data, bot)
