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

from ._baleobject import BaleObject

__all__ = ("Invoice",)


class Invoice(BaleObject):
    """This object represents an invoice or a crowdfunding message in the Bale messenger. Currently, it can only be seen in :attr:`.Message.invoice`.

    Attributes:
        title (:obj:`str`):
            Product or request title.
        description (:obj:`str`):
            Product or request description.
        currency (:obj:`str`):
            Three-letter ISO 4217 currency code.
        total_amount (:obj:`int`):
            Total price of the invoice or crowdfunding message.
        invoice_payload (:obj:`str`, optional):
            Bot specified invoice payload.
    """

    __slots__ = (
        "title",
        "description",
        "currency",
        "total_amount",
        "invoice_payload",
    )

    def __init__(
        self,
        title: str,
        description: str,
        currency: str,
        total_amount: int,
        invoice_payload: str | None = None,
    ) -> None:
        super().__init__()
        self.title = title
        self.description = description
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload

        self._lock()
