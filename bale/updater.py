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

import asyncio
import contextlib
import logging
from collections.abc import Callable, Coroutine
from contextlib import suppress
from typing import TYPE_CHECKING

from ._exceptions import BaleError, InvalidToken, TimeOut
from ._utils.typehint import MISSING, SentinelOrValue

if TYPE_CHECKING:
    from bale import Bot

__all__ = ("Updater",)

_log = logging.getLogger(__name__)


class Updater:
    """This object represents a Updater.

    Attributes:
        bot (:class:`~bale.Bot`):
            The bot used with this Updater.
        interval (:obj:`float` | :obj:`int`):
            The interval in seconds.
    """

    __slots__ = (
        "bot",
        "interval",
        "_last_offset",
        "_running",
        "__lock",
        "__worker_task",
        "__stop_worker_event",
    )

    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self.interval: float | None = None
        self._last_offset: int | None = None
        self._running: bool = False
        self.__worker_task: asyncio.Task[None] | None = None
        self.__stop_worker_event: asyncio.Event | None = None

    @property
    def current_offset(self) -> int | None:
        """:obj:`int`, optional: Represents the last offset in updates. :obj:`None` if Updater is not started."""
        return self._last_offset

    @current_offset.setter
    def current_offset(self, value) -> None:
        if value and not isinstance(value, int):
            raise TypeError(
                "The value of the current offset must be type of int or NoneType"
            )

        self._last_offset = value

    async def setup(self) -> None:
        if self._running:
            raise RuntimeError("Updater is already running")

        self.__stop_worker_event = asyncio.Event()

    async def start_polling(
        self,
        get_updates_timeout: int,
        error_handler: Callable[[Exception], bool] | None = None,
        skip_updates: bool = False,
    ) -> None:
        """
        Starting the process of receiving updates.

        The following events occur in sequence:

        * The status of the updater changes to active.

        * The :func:`on_updater_ready` event is called.

        * A new :class:`asyncio.Task` is created, in which a loop for continuously receiving the remaining updates exists.

        Arguments:
            get_updates_timeout:
                The duration (in seconds) to wait in :ref:`get_updates_method`. If no update is received within this period, an empty response will be returned. Using this parameter reduces the number of requests and improves performance.

            error_handler:
                This function is called when an error occurs in the updater. The function should have a parameter to receive the updater error. The return value of this function is :obj:`bool` and indicates whether the updater can continue or not.

                This function should be written as follows:

                .. code-block:: python

                    from bale import BaleError

                    def getupdates_error_handler(exc: Any) -> bool:
                        if isinstance(exc, BaleError):
                            return False
                        return True

            skip_updates:
                Whether to drop pending updates accumulated while the bot was offline before
                starting the polling process.

        .. versionchanged:: 3.0
            The :paramref:`skip_updates` parameter has been added.
        """
        if self._running:
            raise RuntimeError("Updater is already running")

        if self.bot.http_is_closed():
            raise RuntimeError("HTTPClient is closed")

        self._running = True

        if skip_updates:
            await self._drop_pending_updates()

        self.bot.dispatch("updater_ready")
        _log.debug("Updater started")

        return await self._polling(
            get_updates_timeout=get_updates_timeout,
            getupdates_error_handler=error_handler,
        )

    async def _drop_pending_updates(self) -> None:
        if not self._running:
            raise RuntimeError("Updater is not running")

        if self.bot.http_is_closed():
            raise RuntimeError("HTTPClient is closed")

        _log.debug("Skipping pending updates...")
        try:
            updates = await self.bot.get_updates(offset=-1, limit=1, timeout=0)
            if updates:
                self._last_offset = updates[0].update_id
                _log.debug(
                    "Pending updates skipped. Next offset: %s", self._last_offset + 1
                )
            else:
                _log.debug("No pending updates to skip.")

        except Exception as exc:
            _log.warning("Failed to skip pending updates: %s", exc, exc_info=exc)

    async def _polling(
        self,
        get_updates_timeout: SentinelOrValue[int] = None,
        getupdates_error_handler: Callable[[Exception], bool] | None = None,
    ) -> None:
        async def action_getupdates() -> (
            bool
        ):  # When False is returned, the operation stops.
            offset = self._last_offset + 1 if self._last_offset else MISSING

            updates = await self.bot.get_updates(
                offset=offset,
                timeout=get_updates_timeout,
                request_timeout=35,
                handle_rate_limit=False,
            )

            if updates:
                for update in updates:
                    if self.current_offset is None or (
                        update.update_id
                        > self.current_offset  # This is due to a bug sometimes caused by the Bale servers.
                    ):
                        await self.bot.update_queue.put(update)
                self._last_offset = updates[-1].update_id

            return True

        def default_polling_error_handler(exc: Exception) -> bool:
            if not isinstance(exc, BaleError):
                _log.critical(
                    "Something was happened when we process Update data from bale",
                    exc_info=exc,
                )

            _log.exception(
                "Exception happened when polling for updates. But it was ignored by default error handler.",
                exc_info=exc,
            )
            return True  # so that the updater continues its worker.

        self.__worker_task = asyncio.create_task(
            self.__start_worker(
                action_getupdates,
                getupdates_error_handler or default_polling_error_handler,
            ),
            name="updater:polling_worker",
        )

    async def __start_worker(
        self,
        work_coroutine: Callable[..., Coroutine],
        error_handler: Callable[[Exception], bool | None],
    ) -> None:
        if not self.__stop_worker_event:
            raise RuntimeError(
                "Stop worker event has not been initialized. Please call `setup()` before starting the worker."
            )

        wait_stop_task = asyncio.create_task(self.__stop_worker_event.wait())

        try:
            while self._running and not self.__stop_worker_event.is_set():
                work_task = asyncio.create_task(work_coroutine())

                done, pending = await asyncio.wait(
                    [work_task, wait_stop_task], return_when=asyncio.FIRST_COMPLETED
                )

                for task in pending:
                    if task is not wait_stop_task:
                        task.cancel()
                        with suppress(asyncio.CancelledError):
                            await task  # wait for the task to finish after cancellation

                if wait_stop_task in done:
                    _log.debug("Updater was canceled by stop worker event")
                    break

                try:
                    result = work_task.result()
                    if not result:
                        break
                except asyncio.CancelledError:
                    break
                except InvalidToken:
                    _log.error("Token was invalid")
                    raise
                except TimeOut:
                    interval = 0.0
                except BaleError as exc:
                    _log.debug("Error while Getting Updates: %s", exc)
                    if not error_handler(
                        exc
                    ):  # Does the error handler allow the updater to continue?
                        raise

                    interval = 10.0  # 10 seconds to show errors
                except Exception as exc:
                    _log.exception("Unexpected error inside updater loop: %s", exc)
                    if not error_handler(exc):
                        raise
                    interval = 5.0
                else:  # back interval to normal
                    interval = self.interval or 0.0

                if interval > 0:
                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(
                            self.__stop_worker_event.wait(), interval
                        )
                        break
        finally:
            if not wait_stop_task.done():
                wait_stop_task.cancel()
                with suppress(asyncio.CancelledError):
                    await wait_stop_task

            self._running = False

    async def clear(self) -> None:
        if self.__stop_worker_event:
            self.__stop_worker_event.clear()
        if self.__worker_task and not self.__worker_task.done():
            self.__worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.__worker_task

        self.__worker_task = None

    async def stop(self) -> None:
        """Stop running and Stop ``poll_event`` loop"""
        if not self._running:
            return

        self._running = False

        if self.__stop_worker_event:
            self.__stop_worker_event.set()

        if self.__worker_task and not self.__worker_task.done():
            with suppress(asyncio.TimeoutError, TimeoutError, asyncio.CancelledError):
                await asyncio.wait_for(asyncio.shield(self.__worker_task), 1.5)

        await self.clear()
