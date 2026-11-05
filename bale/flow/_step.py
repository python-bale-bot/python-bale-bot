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

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from .._utils.checkers import iscoroutinefunction, validate_timeout
from .._utils.typehint import MISSING, SentinelOrValue
from ..handlers import UpdateHandler

__all__ = ("Step",)


F = TypeVar("F", bound=Callable[..., Any])

if TYPE_CHECKING:
    from bale.context import Context
    from bale.flow import ConversationFlow


class Step:
    """

    .. versionadded:: 3.0
    """

    __slots__ = ("func", "timeout", "name", "on_error", "additional_data", "_handler")

    def __init__(
        self,
        func: Callable[["Context"], Coroutine[Any, Any, Any]],
        handler: UpdateHandler,
        timeout: SentinelOrValue[float | int | None] = MISSING,
        name: str | None = None,
    ) -> None:
        if not iscoroutinefunction(func):
            raise TypeError(f"{func.__name__} is not a coroutine function")

        timeout = validate_timeout(timeout)

        self.func = func
        self.name = name if name else self._handler.callback.__qualname__
        self.timeout = timeout
        self._handler = handler

    def fallback(self, func: F) -> F:
        self._handler.set_error_callback(func)
        return func

    async def check_new_update(self, context: "Context"):
        return await self._handler.check_new_update(context)

    async def handle_update(self, context: "Context", *args):
        return await self._handler.handle_update(context, *args)

    def __call__(self, *args, **kwargs) -> Any:
        return self._handler.callback(*args, **kwargs)

    def bind(self, base: "ConversationFlow") -> None:
        self._handler._self = base

    def __repr__(self) -> str:
        return f"<Step {self.name} handler={self._handler} timeout={self.timeout}>"
