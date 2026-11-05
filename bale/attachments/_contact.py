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

from .._baleobject import BaleObject

__all__ = ("Contact",)


class Contact(BaleObject):
    """This object shows a Contact.

    Attributes:
        phone_number (:obj:`int`):
            Contact’s phone number.
        first_name (:obj:`str`):
            Contact’s first name.
        last_name (:obj:`str`, optional):
            Contact’s last name.
        user_id (:obj:`int`, optional):
            Contact’s user identifier in Bale.
    """

    __slots__ = ("phone_number", "first_name", "last_name", "user_id")

    def __init__(
        self,
        phone_number: int,
        first_name: str,
        last_name: str | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__()
        self._id = user_id
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

        self._lock()
