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
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context


class BaseMiddleware(ABC):
    """A base class for implementing middlewares.

    To create a new middleware, define a class that inherits from
    :class:`BaseMiddleware` and then register an instance of that class
    with the :class:`~bale.Bot`.

    .. versionadded:: 3.0
    """

    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    async def before_update(self, ctx: "Context") -> bool:
        """
        This method is called before an update is processed. It is responsible
        for performing the required checks and returning a Boolean value.

        If the method returns :obj:`False`, the update is immediately removed from
        the processing pipeline and is considered rejected.

        Returning :obj:`True` is necessary for the update to continue through the
        processing pipeline, but it is not sufficient by itself. Other
        processing conditions may still prevent the update from being handled.

        Important:

            This method is executed for every update. Therefore, its response
            time has a significant impact on the overall performance of the
            application.

            If this method needs to send a request to an external service, keep
            in mind that the request may be sent many times per second. Whenever
            possible, cache the response or the required data to avoid sending
            the same request repeatedly.
        """

    @abstractmethod
    async def after_update(
        self,
        ctx: "Context",
        error: Exception | None = None,
    ) -> None:
        """
        Run after the update has been processed.

        This hook is optional and can be overridden for logging, metrics,
        cleanup, auditing, or error reporting.
        """
        # This hook is intentionally a no-op by default.

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self._name}>"
