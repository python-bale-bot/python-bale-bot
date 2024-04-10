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

from typing import Optional, List, Union
from bale import CallbackQuery, Update
from .basecheck import BaseCheck

__all__ = (
    "CallbackQueryCheck",
    "Data",
    "DATA"
)

# TODO: COMPLETE DOCS

class CallbackQueryCheck(BaseCheck):
    __slots__ = ("for_what",)
    def check_update(self, update: "Update") -> bool:
        target_callback_query: Optional[CallbackQuery] = update.callback_query

        if target_callback_query and self.check(target_callback_query):
            return True
        return False

    async def check(self, callback_query: CallbackQuery) -> bool:
        return callback_query is not None


class Data(CallbackQueryCheck):
    __slots__ = ("strings",)

    def __init__(self, strings: Optional[Union[List[str], str]] = None) -> None:
        super().__init__(
            "Data" + (
                repr(strings) if strings else ""
            )
        )
        if isinstance(strings, str):
            strings = [strings]
        self.strings = strings

    async def check(self, callback_query: CallbackQuery) -> bool:
        if data := callback_query.data:
            if not self.strings or data in self.strings:
                return True

        return False

DATA = Data()