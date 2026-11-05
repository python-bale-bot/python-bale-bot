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
from datetime import datetime
from typing import TYPE_CHECKING

from ._baleobject import BaleObject
from .helpers import parse_time

if TYPE_CHECKING:
    from ._types.transaction import Transaction as TransactionPayload

__all__ = ("Transaction",)


class Transaction(BaleObject):
    """Represents a payment transaction in the `Bale <https://ble.ir>`_ platform.

    This class models the structure of a transaction object returned by the
    :meth:`~Bot.inquire_transaction` API. It includes essential information such as the
    transaction ID, status, user ID, amount, and creation time.

    Attributes:
        id (:obj:`int`):
            Unique identifier of the transaction.
        status (:obj:`str`):
            Indicates the current status of the transaction.
        user_id (:obj:`int`):
            Unique identifier of the user who initiated the transaction.
        amount (:obj:`int`):
            Transaction amount in Rials.
        created_at (:class:`datetime.datetime`):
            A datetime object that indicates when the transaction was created.

    .. versionadded:: 3.0
    """

    __slots__ = ("id", "status", "user_id", "amount", "created_at")

    def __init__(
        self, id: int, status: str, user_id: int, amount: int, created_at: datetime
    ) -> None:
        super().__init__()
        self._id = id
        self.id = id
        self.status = status
        self.user_id = user_id
        self.amount = amount
        self.created_at = created_at

        self._lock()

    @classmethod
    def from_dict(cls, data: "TransactionPayload | None" = None, bot=None):
        """:meta private:"""
        parsed_data = BaleObject.parse_data(data)
        if not parsed_data:
            return None

        parsed_data["created_at"] = parse_time(parsed_data.get("createdAt"))
        parsed_data["user_id"] = parsed_data.pop("userID")

        return super().from_dict(parsed_data, bot)
