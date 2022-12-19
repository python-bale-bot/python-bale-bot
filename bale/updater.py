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
import asyncio
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from bale import Bot, Update

__all__ = (
	"Updater",
	"EventType"
)

class EventType:
	READY = "on_ready"
	UPDATE = "on_update"
	MESSAGE = "on_message"
	CALLBACK = "on_callback"
	MEMBER_CHAT_JOIN = "on_member_chat_join"
	MEMBER_CHAT_LEAVE = "on_member_chat_leave"

class Updater:
	"""This object represents a Bale Bot.

		Attributes:
			bot (:class:`bale.Bot`): The bot used with this Updater.
            update_queue (:class:`asyncio.Queue`): Queue for the updates.
            _last_offset (int | None): Last of Offset for get updates.
            _is_running (bool): get status of updater.
        Args:
            bot (:class:`bale.Bot`): Bot.
        Raises:
            :class:`bale.Error`
    """
	__slots__ = (
		"bot",
		"_last_offset",
		"_is_running",
		"sleep_after_get_updates"
	)

	def __init__(self, bot: "Bot"):
		self.bot = bot
		self._last_offset = None
		self._is_running = False
		self.sleep_after_get_updates = None

	async def start(self, sleep_after_every_get_updates: int = None):
		"""Start poll event function"""
		if self._is_running:
			raise RuntimeError("Updater is running")
		if sleep_after_every_get_updates is not None:
			self.sleep_after_get_updates = sleep_after_every_get_updates
		self._is_running = True
		self.bot.dispatch("ready")
		await self._start()

	async def _start(self):
		"""A loop for get updates in dispatch"""
		if not self._is_running:
			raise RuntimeError("Updater is running")
		while self._is_running:
			if self.bot.is_closed():
				raise RuntimeError("Bot is Closed")

			if self.bot.http.is_closed():
				raise RuntimeError("HTTPClient is Closed")

			if not self._is_running:
				break

			updates = await self.bot.get_updates(offset=self._last_offset)

			for update in updates:
				await self.call_to_dispatch(update)

			self._last_offset = updates[-1].update_id if bool(updates) else self._last_offset

			if self.sleep_after_get_updates is not None:
				await asyncio.sleep(self.sleep_after_get_updates)

	async def call_to_dispatch(self, update: "Update"):
		self.bot.dispatch("update", update)
		if update.type.is_callback_update():
			self.bot.dispatch("callback", update.callback_query)
		elif update.type.is_message_update():
			self.bot.dispatch("message", update.message)
			if update.message.left_chat_member:
				self.bot.dispatch("member_chat_leave", update.message.chat, update.message.left_chat_member)
			for user in update.message.new_chat_members or []:
				self.bot.dispatch("member_chat_join", update.message.chat, user)

	def stop(self):
		"""Stop running and Stop `poll_event` loop"""
		if not self._is_running:
			raise RuntimeError("Updater is not running")

		self._is_running = False
