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
from typing import TYPE_CHECKING, Callable, Coroutine, Optional, NoReturn
from bale import Update
import logging
from .error import InvalidToken, BaleError, NetworkError

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
    """
    __slots__ = (
        "bot",
        "_last_offset",
        "running",
        "interval"
    )

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self._last_offset: Optional[int] = None
        self.running: bool = False
        self.interval: Optional[float] = None

    @property
    def current_offset(self) -> Optional[int]:
        """Optional[:class:`int`]: Represents the last offset in updates. ``None`` if Updater is not started"""
        return self._last_offset

    async def start(self):
        """Start poll event function"""
        if self.running:
            raise RuntimeError("Updater is running")
        _log.debug("Updater is in the pre-start!")
        self.bot.dispatch("before_ready")
        await self.polling()

    async def polling(self) -> NoReturn:
        if self.running:
            raise RuntimeError("Updater is running")

        if self.bot.http_is_closed():
            raise RuntimeError("HTTPClient is Closed")

        self.running = True
        self.bot.dispatch("ready")
        _log.debug("Updater is started! (polling)")

        try:
            await self._polling()
        except Exception as exc:
            self.running = False
            raise exc

    async def _polling(self) -> NoReturn:
        async def action_getupdates() -> bool:
            try:
                updates = await self.bot.get_updates(offset=self._last_offset)
            except BaleError as exc:
                raise exc
            except Exception as exc:
                _log.critical("Somthing was happened when we process Update data from bale", exc_info=exc)
                return True

            if updates:
                for update in updates:
                    await self.process_update(update)
                self._last_offset = updates[-1].update_id

            return True

        def getupdates_error(exc) -> NoReturn:
            _log.exception("Exception happened when polling for updates.", exc_info=exc)

        await self._network_loop_retry(
                action_getupdates,
                getupdates_error
            )

    async def _network_loop_retry(self, action_cb: Callable[..., Coroutine], on_error_cb: Callable) -> NoReturn:
        try:
            while self.running:
                try:
                    if not await action_cb():
                        break

                except InvalidToken as exc:
                    raise exc

                except NetworkError as exc:
                    raise exc

                except BaleError as exc:
                    on_error_cb(exc)

                if self.interval:
                    await asyncio.sleep(self.interval)

        except asyncio.CancelledError:
            _log.debug("Get Updater Loop was cancelled!")

    async def process_update(self, update: "Update"):
        self.bot.dispatch("update", update)
        if update.callback_query:
            self.bot.dispatch("callback", update.callback_query)
        elif update.message:
            self.bot.dispatch("message", update.message)
            if update.message.successful_payment:
                self.bot.dispatch("successful_payment", update.message.successful_payment)
            if update.message.new_chat_members:
                for user in update.message.new_chat_members:
                    self.bot.dispatch("member_chat_join", update.message, update.message.chat, user)
            if update.message.left_chat_member:
                self.bot.dispatch("member_chat_leave", update.message, update.message.chat, update.message.left_chat_member)
        elif update.edited_message:
            self.bot.dispatch("message_edit", update.edited_message)

    async def stop(self):
        """Stop running and Stop `poll_event` loop"""
        self.running = False
