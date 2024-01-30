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

from typing import Callable, Tuple, Optional

from bale import Update, CallbackQuery
from .basehandler import BaseHandler


class CallbackQueryHandler(BaseHandler):
    """This object shows a Callback Query Handler.
    It's a handler class to handle Callback Queries.

    Parameters
    ----------
        check: Optional[Callable[["Update"], bool]]
            The check function for this handler.

            .. hint::
                Called in :meth:`check_new_update`, when new update confirm. This checker indicates whether the Update should be covered by the handler or not.
    """
    __slots__ = (
        "check",
    )

    def __init__(self, check: Optional[Callable[["Update"], bool]] = None):
        super().__init__()
        if not check:
            check = lambda *_: True

        self.check = check

    def check_new_update(self, update: "Update") -> Optional[Tuple["CallbackQuery"]]:
        if not update.callback_query:
            return None

        if self.check and not self.check(update):
            return None

        return (
            update.callback_query,
        )
