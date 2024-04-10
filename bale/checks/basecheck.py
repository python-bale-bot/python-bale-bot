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

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Update

__all__ = ("BaseCheck",)

class BaseCheck:
    __slots__ = ("name",)
    def __init__(self, name: Optional[str] = None):
        self.name = name if name else self.__class__.__name__

    def check_update(self, update: "Update") -> bool:
        return True

    def __and__(self, other: "BaseCheck") -> "BaseCheck":
        return _MergedCheck(self, and_check=other)

    def __or__(self, other: "BaseCheck") -> "BaseCheck":
        return _MergedCheck(self, or_check=other)

    def __invert__(self) -> "BaseCheck":
        return _InvertedCheck(self)

    def __repr__(self) -> str:
        return self.name

class _MergedCheck(BaseCheck):
    __slots__ = (
        "base_check",
        "and_check",
        "or_check"
    )
    def __init__(self, base_check: BaseCheck, and_check: Optional[BaseCheck] = None, or_check: Optional[BaseCheck] = None):
        super().__init__()
        if and_check and or_check:
            raise ValueError(
                "You can use and_check and or_check together"
            )

        self.base_check = base_check
        self.and_check = and_check
        self.or_check = or_check

        self.name = f"MergedCheck({base_check}, {and_check or or_check})"

    def check_update(self, update: "Update") -> bool:
        base_check = self.base_check.check_update(update)

        if self.and_check and base_check:
            return self.and_check.check_update(update)
        elif self.or_check:
            return self.or_check.check_update(update)

        return False

class _InvertedCheck(BaseCheck):
    __slots__ = ("base_check",)
    def __init__(self, base_check: BaseCheck):
        super().__init__()
        self.base_check = base_check

    def check_update(self, update: "Update") -> bool:
        return not self.base_check.check_update(update)
