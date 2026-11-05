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
    from .webapp import WebAppInfo

__all__ = (
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "KeyboardButton",
    "ReplyKeyboardMarkup",
)


class CopyTextButton(TypedDict):
    text: str


class InlineKeyboardButton(TypedDict, total=False):
    text: str
    url: NotRequired[str | None]
    callback_data: NotRequired[str | None]
    web_app: NotRequired["WebAppInfo | None"]
    copy_text: NotRequired["CopyTextButton | None"]
    style: NotRequired[str | bool]


class KeyboardButton(TypedDict, total=False):
    text: str
    request_contact: NotRequired[bool | None]
    request_location: NotRequired[bool | None]
    web_app: NotRequired["WebAppInfo | None"]
    style: NotRequired[str | bool]


class InlineKeyboardMarkup(TypedDict):
    inline_keyboard: list[list[InlineKeyboardButton]]


class ReplyKeyboardMarkup(TypedDict):
    keyboard: list[list[KeyboardButton]]
    resize_keyboard: NotRequired[bool]
