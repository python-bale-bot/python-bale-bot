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

from ._baleobject import BaleObject
from ._user import User
from ._utils.typehint import MISSING, SentinelOrValue

if TYPE_CHECKING:
    from bale import Bot

    from ._types.precheckoutquery import \
        PreCheckoutQuery as PreCheckoutQueryPayload

__all__ = ("PreCheckoutQuery",)


class PreCheckoutQuery(BaleObject):
    """This object represents a pre-checkout query; i.e., a payment that the bot must verify before it is finalized. This query must be answered within a maximum of 10 seconds, otherwise the transaction will be canceled.

    Important:
        This update is received only for wallet-based payments, and receiving this object does not mean the payment is complete. The payment is finalized only after receiving a message containing a :class:`.SuccessfulPayment` (:attr:`Message.successful_payment`) object, indicating that the transaction is settled

    Attributes:
        id (:obj:`str`):
            Unique identifier for this query.
        from_user (:class:`~bale.User`):
            User who sent the query.
        currency (:obj:`str`, optional):
            Three-letter ISO 4217 currency code (``IRR`` for Rial).
        total_amount (:obj:`int`, optional):
            Total price in the smallest units of the currency.
        invoice_payload (:obj:`str`, optional):
            Bot specified invoice payload sent during the payment request in the :paramref:`.Bot.send_invoice.invoice_payload` parameter.

    .. versionadded:: 3.0
    """

    __slots__ = ("id", "from_user", "currency", "total_amount", "invoice_payload")

    def __init__(
        self,
        id: str,
        from_user: "User",
        currency: str | None = None,
        total_amount: int | None = None,
        invoice_payload: str | None = None,
    ) -> None:
        super().__init__()
        self._id = id
        self.id = id
        self.from_user = from_user
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload

        self._lock()

    async def answer(self, ok: bool, error_message: SentinelOrValue[str] = MISSING):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await pre_checkout_query.answer(True)

        .. versionadded:: 3.0
        """
        return await self.get_bot().answer_pre_checkout_query(
            self.id, ok, error_message
        )

    async def inquire(self):
        """|shortcut|

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                await pre_checkout_query.inquire()

        .. versionadded:: 3.0
        """
        return await self.get_bot().inquire_transaction(self.id)

    @classmethod
    def from_dict(
        cls, data: "PreCheckoutQueryPayload | None" = None, bot: "Bot | None" = None
    ):
        """:meta private:"""
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["from_user"] = User.from_dict(data.pop("from", None), bot)

        return super().from_dict(data, bot)
