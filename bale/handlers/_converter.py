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
from typing import Literal, TypeVar, TYPE_CHECKING, Generic
from re import compile as re_compile

if TYPE_CHECKING:
    from bale import ChatFullInfo, User
    from bale.context import Context

T_co = TypeVar("T_co", covariant=True)
NUMERIC_ID_PATTERN = re_compile(r"^[0-9]{5,}$")
USERNAME_PATTERN = re_compile(r"^[a-zA-z][a-zA-Z_0-9]{4,31}]$")

__all__ = ("Converter", "ChatConverter", "UserConverter")


class Converter(Generic[T_co]):
    async def __call__(self, context: "Context", raw: str) -> T_co | Literal[False]:
        ...


class ChatConverter(Converter["ChatFullInfo"]):
    async def __call__(self, context: "Context", raw: str) -> "ChatFullInfo | Literal[False]":
        bot = context.bot
        if raw.startswith("@"):
            raw = raw.removeprefix("@")

        if not (
            NUMERIC_ID_PATTERN.fullmatch(raw) or
            USERNAME_PATTERN.fullmatch(raw)
        ):
            return False

        chat = await bot.get_chat(raw)
        return chat if chat is not None else False


class UserConverter(Converter["User"]):
    async def __call__(self, context: "Context", raw: str) -> "User | Literal[False]":
        bot = context.bot
        if NUMERIC_ID_PATTERN.fullmatch(raw):
            return False

        user = await bot.get_user(raw)
        return user if user is not None else False
