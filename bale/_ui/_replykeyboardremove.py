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

from .._baleobject import BaleObject

__all__ = ("ReplyKeyboardRemove",)


class ReplyKeyboardRemove(BaleObject):
    """Used to remove the bottom chat keyboard entirely from the user's view.

    .. versionadded:: 3.0
    """

    __slots__ = ()

    def to_dict(self) -> dict[str, bool]:
        return {"remove_keyboard": True}
