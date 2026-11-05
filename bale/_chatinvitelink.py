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
from typing import TYPE_CHECKING

from ._baleobject import BaleObject

if TYPE_CHECKING:
    from bale import User

__all__ = ("ChatInviteLink",)


class ChatInviteLink(BaleObject):
    """This object represents a chat invite link.

    Equality conditions:
        1. The second object must be an instance of :class:`ChatInviteLink`.
        2. Both invite link properties must be identical (:attr:`invite_link`).

    Attributes:
        invite_link (:obj:`str`):
            Invite link.
        creator (:class:`.User`):
            User who created the link.
        creates_join_request (:obj:`bool`):
            If :obj:`True`, users joining via this link must be approved by administrators.

    .. versionadded:: 3.0
    """

    __slots__ = ("invite_link", "creator", "creates_join_request")

    def __init__(
        self, invite_link: str, creator: "User", creates_join_request: bool
    ) -> None:
        super().__init__()
        self._id = invite_link
        self.invite_link = invite_link
        self.creator = creator
        self.creates_join_request = creates_join_request

        self._lock()

    def __str__(self) -> str:
        return self.invite_link
