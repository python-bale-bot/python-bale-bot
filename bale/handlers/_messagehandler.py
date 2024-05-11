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

from bale import Update, Message
from bale.checks import BaseCheck
from ._basehandler import BaseHandler


class MessageHandler(BaseHandler):
    """This object shows a Message Handler.
    It's a handler class to handle Messages.

    Parameters
    ----------
        check: Callable, optional
            The check for this handler.

            .. hint::
                Called in :meth:`check_new_update`, when new update confirm. This checker indicates whether the Update should be covered by the handler or not.
    """
    __slots__ = ("check",)

    def __init__(self, check: Optional[BaseCheck] = None) -> None:
        super().__init__()

        if check and not isinstance(check, BaseCheck):
            raise TypeError(
                "check param must be type of BaseCheck"
            )

        self.check = check

    async def check_new_update(self, update: "Update") -> Optional[Tuple["Message"]]:
        if update.message is not None and (
                not self.check or await self.check.check_update(update)
        ):
            return (
                update.message,
            )

        return None
