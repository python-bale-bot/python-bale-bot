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

from typing import Any

__all__ = ("ResponseParameters",)


class ResponseParameters:
    """Describes why a request was unsuccessful.

    Parameters
    ----------
        retry_after: :obj:`float`
            The number of seconds left to wait before the request can be repeated.

    .. versionadded:: 3.0
    """

    __slots__ = ("retry_after",)

    def __init__(self, retry_after: float | None = None):
        self.retry_after: float | None = retry_after

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ResponseParameters | None":
        if not data:
            return None

        return cls(retry_after=data.get("retry_after"))
