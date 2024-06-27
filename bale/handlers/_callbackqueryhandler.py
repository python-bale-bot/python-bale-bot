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

from typing import Tuple, Optional

from bale import Update, CallbackQuery
from bale.checks import BaseCheck
from ._basehandler import BaseHandler


class CallbackQueryHandler(BaseHandler):
    """This object shows a Callback Query Handler.
    It's a handler class to handle Callback Queries.
    """
    __slots__ = ("check",)

    def __init__(self, check: Optional[BaseCheck] = None):
        super().__init__()

        if check and not isinstance(check, BaseCheck):
            raise TypeError(
                "check param must be type of BaseCheck"
            )

        self.check = check

    async def check_new_update(self, update: "Update") -> Optional[Tuple["CallbackQuery"]]:
        if update.callback_query and (
            self.check and await self.check.check_update(update)
        ):
            return (
                update.callback_query,
            )

        return None
