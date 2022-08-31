"""MIT License

    Copyright (c) 2022 kian Ahmadian

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
from typing import TYPE_CHECKING, List
import asyncio
if TYPE_CHECKING:
	from bale import Bot, Update

__all__ = (
	"Updater",
)

class Updater:
	"""This object represents a Bale Bot.

        Args:
            bot (:class:`bale.Bot`): Bot.
            update_queue (:class:`asyncio.Queue`): Update queue.
        Raises:
            :class:`bale.Error`
    """
	__slots__ = (
		"bot",
		"update_queue",
		"_last_offset",
		"__lock",
		"_is_running"
	)

	def __init__(self, bot: "Bot", update_queue: asyncio.Queue):
		self.bot = bot
		self.update_queue = update_queue
		self._last_offset = None
		self.__lock = asyncio.Lock()
		self._is_running = False

	def start(self):
		if self._is_running:
			raise RuntimeError("Updater is running")

		self._is_running = True

	def get_updates(self):
		while self._is_running:
			async with self.__lock:
				if self.bot.close():
					raise RuntimeError("Bot is Closed!")

				if not self._is_running:
					raise RuntimeError("Updater is not running")

				updates: List["Update"] = await self.bot.get_updates(offset=self._last_offset)

				for update in updates:
					self.bot.dispatch("update", update)

				self._last_offset = updates[0].update_id if bool(updates) else self._last_offset

	def stop(self):
		if not self._is_running:
			raise RuntimeError("Updater is not running")

		self._is_running = False