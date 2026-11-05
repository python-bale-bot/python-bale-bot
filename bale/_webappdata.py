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
from ._baleobject import BaleObject

__all__ = ("WebAppData",)


class WebAppData(BaleObject):
    """This object represents data sent from a Mini App.

    Attributes:
        data (:obj:`str`):
            The data sent. It is worth noting that a malicious client can send arbitrary and invalid data in this field, so validation on the bot's side is recommended.

    .. versionadded:: 3.0
    """

    __slots__ = ("data",)

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data = data

        self._lock()
