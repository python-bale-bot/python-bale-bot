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
import asyncio
import time
from logging import getLogger
from typing import TYPE_CHECKING, Any, Coroutine

if TYPE_CHECKING:
    from bale import Bot


__all__ = ("ChatActionContextManager",)


class ChatActionContextManager:
    """
    A context manager to continuously send chat actions (e.g., typing...) to a chat
    while performing asynchronous operations. Designed for use with ``async with`` blocks.

    This class ensures that the chat action is sent in a loop at fixed intervals (e.g., every 5 seconds)
    until the context exits.

    Example usage:

    .. code-block:: python

        from bale.constants import ChatAction

        async with ChatActionContextManager(chat_id, ChatAction.TYPING, bot):
            await some_long_running_task()

    Arguments:
        chat_id:
            The identifier of the chat (user ID or group ID) to which the action is sent.
        action:
            The name of the chat action to send. Example: "typing", "upload_photo", etc.
        bot:
            The bot instance responsible for sending the chat action.
        interval:
            The interval (in seconds) between repeated chat action messages. Default is ``5.0`` seconds.
        kwargs:
            Additional keyword arguments for future extension (currently unused).
    """

    _log = getLogger("chatactioncontextmanager")

    __slots__ = (
        "__action_worker",
        "_chat_id",
        "_action",
        "_bot",
        "_interval",
        "__lock",
        "__stop_worker_event",
    )

    def __init__(
        self,
        chat_id: int | str,
        action: str,
        bot: "Bot",
        interval: float = 5.0,
        **kwargs,
    ):
        self._chat_id = chat_id
        self._action = action
        self._bot = bot
        self._interval = interval
        self.__lock = asyncio.Lock()
        self.__action_worker: asyncio.Task[None] | None = None
        self.__stop_worker_event = asyncio.Event()

    def _send_chat_action_coro(self) -> Coroutine[Any, Any, bool]:
        return self._bot.send_chat_action(self._chat_id, self._action)

    async def _send_action_loop_retry(self):
        while not self.__stop_worker_event.is_set():
            self._log.debug("Send chat action %s to %s", self._action, self._chat_id)

            try:
                await self._send_chat_action_coro()
            except Exception as exc:
                self._log.debug("Failed to send chat action: %s", exc, exc_info=True)

            start_time = time.monotonic()
            interval = max(
                0.0, self._interval - (time.monotonic() - start_time)
            )  # don't use wasted time in interval

            if interval:
                try:
                    await asyncio.wait_for(self.__stop_worker_event.wait(), interval)
                    break
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(0)  # :D

    def __await__(self):
        # await x
        return self._send_chat_action_coro().__await__()

    async def _start(self):
        async with self.__lock:
            self.__stop_worker_event.clear()
            self.__action_worker = asyncio.create_task(
                self._send_action_loop_retry(),
                name=f"ChatActionContextManager:{self._chat_id}:{self._action}",
            )

    async def _stop(self):
        async with self.__lock:
            if not self.__stop_worker_event.is_set():
                self.__stop_worker_event.set()

    async def __aenter__(self) -> "ChatActionContextManager":
        # async with x:
        await self._start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._stop()
