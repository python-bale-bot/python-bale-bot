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
from __future__ import annotations
from bale import BaleObject
from typing import Optional

__all__ = (
    "SuccessfulPayment",
)


class SuccessfulPayment(BaleObject):
    """
    This object contains basic information about a successful payment.

    Attributes
    ----------
        currency: :class:`str`
            The currency in which the transaction was made.
        total_amount: :class:`int`
            The total sum of the transaction amount.
        invoice_payload: Optional[:class:`str`]
            Bot specified invoice payload.
        shipping_option_id: Optional[:class:`str`]
            Identifier of the shipping option chosen by the user.
    """
    __slots__ = (
        "currency",
        "total_amount",
        "invoice_payload",
        "shipping_option_id"
    )

    def __init__(self, currency: str, total_amount: int, invoice_payload: Optional[str] = None, shipping_option_id: Optional[str] = None):
        super().__init__()
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id

        self._lock()

    @property
    def payload(self) -> Optional[str]:
        """Aliases for :attr:`invoice_payload`"""
        return self.invoice_payload
