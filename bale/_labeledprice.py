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

__all__ = ("LabeledPrice",)


class LabeledPrice(BaleObject):
    """This object represents a portion of the price for goods or services.

    Attributes:
        label (:obj:`str`, optional):
            Portion label or Label price (e.g. Grade 1 honey, shipping cost, or tax).
        amount (:obj:`int`, optional):
            Price of the portion in Rials. Must be an integer.
    """

    __slots__ = ("label", "amount")

    def __init__(self, label: str | None = None, amount: int | None = None) -> None:
        super().__init__()
        self._id = (label, amount)
        self.label = label
        self.amount = amount

        self._lock()
