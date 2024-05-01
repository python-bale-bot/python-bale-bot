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
	"Invoice",
)

class Invoice(BaleObject):
	"""This object shows Invoice

    Attributes
    ----------
        title: str
        	Product name.
        description: str
        	Product description.
        start_parameter: str
        	Unique bot deep-linking parameter that can be used to generate this invoice.
        currency: str
        	Three-letter ISO 4217 currency code.
        total_amount: int
        	Total price in the smallest units of the currency (integer, not float/double).
    """
	__slots__ = (
		"title",
		"description",
		"start_parameter",
		"currency",
		"total_amount"
	)
	def __init__(self, title: str, description: str, start_parameter: str, currency: str, total_amount: int):
		super().__init__()
		self.title = title
		self.description = description
		self.start_parameter = start_parameter
		self.currency = currency
		self.total_amount = total_amount

		self._lock()