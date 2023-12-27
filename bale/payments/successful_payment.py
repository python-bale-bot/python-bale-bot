"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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
