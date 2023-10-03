"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot, Update

__all__ = (
    "Updater"
)

class Updater:
    """This object represents a Bale Bot.

        Attributes:
            bot (:class:`bale.Bot`): The bot used with this Updater.
            _last_offset (int | None): Last of Offset for get updates.
            _is_running (bool): get status of updater.
        Args:
            bot (:class:`bale.Bot`): The Bot Object.
    """
    __slots__ = (
        "bot",
        "_last_offset",
        "running",
        "__lock",
        "interval"
    )

    def __init__(self, bot: "Bot"):
        self.bot = bot
        self._last_offset: Optional[int] = None
        self.running = False
        self.__lock = asyncio.Lock()
        self.interval = None

    @property
    def current_offset(self) -> Optional[int]:
        """Optional[:class:`int`]: Represents the last offset in updates. ``None`` if Updater is not started"""
        return self._last_offset

    async def start(self):
        """Start poll event function"""
        if self.running:
            raise RuntimeError("Updater is running")
        self.bot.dispatch("before_ready")
        await self.polling()

    async def polling(self) -> NoReturn:
        async with self.__lock:
            if self.running:
                raise RuntimeError("Updater is running")

            if self.bot.http.is_closed():
                raise RuntimeError("HTTPClient is Closed")

            self.running = True
            self.bot.dispatch("ready")

            try:
                await self._polling()
            except Exception as exc:
                self.running = False
                raise exc

    async def _polling(self):
        self.bot.dispatch("ready")
        await self.action_getupdates()

    async def action_getupdates(self):
        while self._is_running:
            try:
                updates = await self.bot.get_updates(offset=self._last_offset)
            except Exception as exc:
                await self.bot.on_error("getUpdates", exc)
            else:
                if updates:
                    for update in updates:
                        await self.call_to_dispatch(update)

                    self._last_offset = updates[-1].update_id
                if self.interval:
                    await asyncio.sleep(self.interval)

    async def call_to_dispatch(self, update: "Update"):
        self.bot.dispatch("update", update)
        if update.type == "callback":
            self.bot.dispatch("callback", update.callback_query)
        elif update.type == "message":
            self.bot.dispatch("message", update.message)
            if update.message.successful_payment:
                self.bot.dispatch("successful_payment", update.message.successful_payment)
            if update.message.left_chat_member:
                self.bot.dispatch("member_chat_leave", update.message, update.message.chat, update.message.left_chat_member)
            for user in update.message.new_chat_members or []:
                self.bot.dispatch("member_chat_join", update.message, update.message.chat, user)
        elif update.type == "edited_message":
            self.bot.dispatch("edited_message", update.edited_message)

    async def stop(self):
        """Stop running and Stop `poll_event` loop"""
        async with self.__lock:
            if not self.running:
                raise RuntimeError("Updater is not running")

            self.running = False
