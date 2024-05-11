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

import re
from typing import Union, Pattern, Tuple, Optional, Match

from bale import Update, Message
from ._basehandler import BaseHandler


class RegexHandler(BaseHandler):
    """This object shows a Regex Handler.
    It's a handler class to handle Messages.

    """
    __slots__ = ("pattern",)

    def __init__(self, pattern: Union[str, Pattern[str]]):
        super().__init__()

        if isinstance(pattern, str):
            pattern: Pattern[str] = re.compile(pattern)
        self.pattern: Pattern = pattern

    async def check_new_update(self, update: "Update") -> Optional[Tuple["Message", Match[str]]]:
        if update.message is not None and (
            (match := self.pattern.match(update.message.text))
        ):
            return (
                update.message, match
            )

        return None
