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
from ._baleobject import BaleObject

__all__ = ("WebAppInfo",)


class WebAppInfo(BaleObject):
    """This object represents information about a Mini App.

    Equality conditions:
        1. The second object must be an instance of the :class:`WebAppInfo` class.
        2. Both must have the same Mini App URL (:attr:`url`).

    Attributes:
        url (:obj:`str`):
            An HTTPS URL of a Web App to be opened with additional data as specified in Initializing Web Apps.

    .. versionadded:: 3.0
    """

    __slots__ = ("url",)

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url
        self._id = (url,)

        self._lock()
