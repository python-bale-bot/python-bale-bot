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
from typing import TYPE_CHECKING, Optional
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
		"__lock",
		"interval",
		"__polling_task"
	)

	def __init__(self, bot: "Bot"):
		self.bot = bot
		self._last_offset = None
		self._is_running = False
		self.__lock = asyncio.Lock()
		self.interval = None
		self.__polling_task: Optional[asyncio.Task] = None

	async def start(self, sleep_after_every_get_updates: int = 0.0):
		"""Start poll event function"""
		if self._is_running:
			raise RuntimeError("Updater is running")
		self.interval = sleep_after_every_get_updates
		self.bot.dispatch("before_ready")
		await self.polling()

	async def polling(self):
		async with self.__lock:
			if not self._is_running:
				raise RuntimeError("Updater is running")

			if self.bot.http.is_closed():
				raise RuntimeError("HTTPClient is Closed")

			self._is_running = True

			try:
				await self._polling()
			except Exception as exc:
				self._is_running = False

	async def _polling(self):
		self.__polling_task = asyncio.create_task(self.action_getupdates(), name = "getUpdates")
		self.bot.dispatch("ready")

	async def action_getupdates(self):
		while self._is_running:
			try:
				updates = await self.bot.get_updates()
				for update in updates:
					await self.call_to_dispatch(update)

				self._last_offset = updates[-1].update_id if bool(updates) else self._last_offset
				await asyncio.sleep(self.interval)
			except Exception as exc:
				await self.bot.on_error("getUpdates", exc)

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
