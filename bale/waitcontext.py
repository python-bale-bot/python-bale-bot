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
from bale import Update
from bale.checks import BaseCheck

class WaitContext:
    __slots__ = (
        "_check",
        "_key",
        "_update"
    )
    def __init__(self, key: str, check: "BaseCheck", update: "Update") -> None:
        self._key = key
        self._check = check
        self._update = update

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, _: str) -> None:
        raise RuntimeError(
            "You can not assign a new value to key."
        )

    @property
    def check(self) -> "BaseCheck":
        return self._check

    @check.setter
    def check(self, _: "BaseCheck"):
        raise RuntimeError(
            "You can not assign a new value to check."
        )

    @property
    def update(self) -> "Update":
        return self._update

    @update.setter
    def update(self, _: "Update") -> None:
        raise RuntimeError(
            "You can not assign a new value to update."
        )

