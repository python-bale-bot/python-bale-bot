#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .callbackquery import CallbackQuery
    from .message import Message
    from .precheckoutquery import PreCheckoutQuery

__all__ = ("Update",)


class Update(TypedDict, total=False):
    update_id: int
    message: NotRequired["Message | None"]
    edited_message: NotRequired["Message | None"]
    callback_query: NotRequired["CallbackQuery | None"]
    pre_checkout_query: NotRequired["PreCheckoutQuery | None"]
