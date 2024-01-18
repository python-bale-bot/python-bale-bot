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

__all__ = (
	"LabeledPrice",
)

class LabeledPrice(BaleObject):
	"""This object shows a LabeledPrice.

    Attributes
    ----------
        label: Optional[:class:`str`]
            Label Price.
        amount: Optional[:class:`int`]
            Amount Price.
    """
	__slots__ = ("label", "amount")

	def __init__(self, label: str = None, amount: int = None):
		super().__init__()
		self.label = label
		self.amount = amount

		self._lock()