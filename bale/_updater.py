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
import asyncio
import logging
from typing import TYPE_CHECKING, Callable, Coroutine, Any, Optional

from ._error import InvalidToken, BaleError, TimeOut

if TYPE_CHECKING:
    from bale import Bot

__all__ = (
    "Updater"
)

_log = logging.getLogger(__name__)

class Updater:
    """This object represents a Bale Bot.

        Attributes:
            bot (:class:`bale.Bot`): The bot used with this Updater.
            interval (:obj:`float` | :obj:`int`): The interval in seconds.
    """
    __slots__ = (
        "bot",
        "_last_offset",
        "_running",
        "__worker_task",
        "__stop_worker_event",
        "__lock",
        "interval"
    )

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self._last_offset: Optional[int] = None
        self._running: bool = False
        self.interval: Optional[float] = None
        self.__lock: asyncio.Lock = asyncio.Lock()
        self.__worker_task: Optional[asyncio.Task] = None
        self.__stop_worker_event: Optional[asyncio.Event] = None

    @property
    def current_offset(self) -> Optional[int]:
        """:obj:`int`, optional: Represents the last offset in updates. ``None`` if Updater is not started"""
        return self._last_offset

    async def setup(self):
        """setup the updater object"""
        # TODO: FILL THE DOCSTRINGS
        if self._running:
            raise RuntimeError(
                "Updater already is running!"
            )

        self.__stop_worker_event = asyncio.Event()

    async def start_polling(self) -> None:
        if self._running:
            raise RuntimeError("Updater is running")

        if self.bot.http_is_closed():
            raise RuntimeError("HTTPClient is Closed")

        self._running = True
        self.bot.dispatch("ready")
        _log.debug("Updater is started!")

        try:
            await self._polling()
        except Exception as exc:
            self._running = False
            raise exc

    async def _polling(self) -> None:
        async def action_getupdates() -> bool: # When False is returned, the operation stops.
            try:
                updates = await self.bot.get_updates(offset=self._last_offset)
            except BaleError as exc: # includes InvalidToken, RateLimited, ...
                raise exc
            except Exception as exc:
                _log.critical("Somthing was happened when we process Update data from bale", exc_info=exc)
                return True

            if updates:
                for update in updates:
                    await self.bot.update_queue.put(update) # we need to clear the queue and subsequently handle its updates!
                self._last_offset = updates[-1].update_id

            return True

        def getupdates_error(exc: Any) -> bool:
            _log.exception("Exception happened when polling for updates.", exc_info=exc)
            return False

        self.__worker_task = asyncio.create_task(
            self.__start_worker(
                action_getupdates,
                getupdates_error
            ), name="Get Updates Worker Task"
        )

    async def __start_worker(self, work_coroutine: Callable[..., Coroutine], error_handler: Callable[[BaleError], bool]) -> None:
        interval = self.interval

        while self._running:
            try:
                if self.__stop_worker_event.is_set() or not await work_coroutine():
                    break
            except InvalidToken as exc:
                _log.error('Token was invalid')
                raise exc
            except TimeOut:
                interval = 0
            except BaleError as exc:
                _log.debug("Error while Getting Updates: %s", exc)
                if not error_handler(exc): # Does the error handler allow the updater to continue?
                    raise exc

                interval = 10 # 10 seconds to show errors
            else: # back interval to normal
                interval = self.interval

            if interval:
                await asyncio.sleep(interval)

    async def stop(self):
        """Stop running and Stop `poll_event` loop"""
        if self._running:
            self.__worker_task.cancel()

        self.__worker_task = None
        self._running = False
