#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.#  This software is licensed under the GNU General Public License v2.0.
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
import time
from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

from bale import HandlerOnCooldown

from ..context import Context

if TYPE_CHECKING:
    from bale.constants import CooldownTarget

    Target: TypeAlias = Callable[[Context], Any] | CooldownTarget

Func_T = TypeVar("Func_T", bound=Callable[..., Any])

__all__ = ("Cooldown", "cooldown")


class Cooldown:
    """With this class, it is possible to set a limit on the number of times a handler can be used within a specific time frame. For example, using this feature, you can restrict a handler to be used only 5 times every 30 seconds per user.

    Arguments:
        per:
            The maximum number of times the function can be called within the :paramref:`rate` interval.
        rate:
            The interval during which the function can be called up to :paramref:`per` times.

            Hint:
                This parameter also accepts a :class:`datetime.timedelta` object.
        target:
            A function that takes a single parameter of type :class:`~bale.context.Context` and returns an output, which is the key itself.

            Each time a handler is about to be executed with a :class:`~bale.context.Context` object, this function converts the context into a key, and the rate limits are checked for that key.

            Note:
                If you intend to create a new rate limit instead of using the default ones (user, chat, etc.), consider the following points:

                * Since this function runs for every incoming message, it is expected to return the key as quickly as possible.

    Types of Limitations
    ====================

    To better assist in selecting a target, you can use the following default limitations:

    .. list-table::
       :widths: 20 60 60
       :header-rows: 1
       :align: center

       * - Target
         - How the Limitation Works
         - Example (Only the Target Differs)
       * - User
         - This limitation is based on the user's unique identifier.
         - Each user can use the specified handler only twice every 20 seconds.
       * - Chat
         - This limitation is based on the unique identifier of the chat.
         - In each chat, the specified handler can be used only twice every 20 seconds.
       * - Chat Member
         - This limitation is based on a combination of the user's unique identifier and the chat identifier. Together, they form a single key.
         - Each chat member can use the specified handler only twice every 20 seconds.

    .. versionadded:: 3.0
    """

    __slots__ = ("per", "rate", "_target", "_cache")

    def __init__(
        self,
        per: int,
        rate: timedelta | float | int,
        target: "Target",
    ) -> None:
        if isinstance(rate, timedelta):
            rate = rate.total_seconds()

        self.per = per
        self.rate = rate
        self._target = target
        self._cache: dict[Any, tuple[int, float]] = {}

    def _cleanup(self, current: float) -> None:
        dead_keys = [
            key
            for key, (_, start_time) in self._cache.items()
            if current >= (start_time + self.rate)
        ]
        for key in dead_keys:
            del self._cache[key]

    def update_rate_limit(self, context: Context) -> None:
        """It is the first function called by specialized handlers to check the context's limitations.

        Arguments:
            context:
                The Context.
        """
        current = time.time()
        self._cleanup(current)

        key = self.get_key(context)

        tokens, start_time = self._cache.get(key, (0, current))

        if current >= (start_time + self.rate):
            tokens = 0
            start_time = current

        if tokens >= self.per:
            retry_after = (start_time + self.rate) - current
            raise HandlerOnCooldown(self, context, max(0.0, retry_after))

        self._cache[key] = (tokens + 1, start_time)

    def get_key(self, context: Context) -> Any:
        """
        Arguments:
            context:
                The Context.

        Returns:
             This function is executed when the :class:`~bale.context.Context` object is about to be converted into a key. Therefore, its responsibility is to return the key so that the limits for that key can be checked in subsequent actions.
        """
        return self._target(context)

    def reset(self, key: Any = None) -> None:
        if key is None:
            self._cache.clear()
        else:
            self._cache.pop(key, None)


def cooldown(
    per: int,
    rate: timedelta | float | int,
    target: "Target",
):
    cooldown_obj = Cooldown(per, rate, target)

    def wrapper(func: Func_T) -> Func_T:
        setattr(func, "__cooldown__", cooldown_obj)
        return func

    return wrapper
