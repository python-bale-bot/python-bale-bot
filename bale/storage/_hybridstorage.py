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
from __future__ import annotations

import asyncio
import logging
from abc import ABC
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Literal

from ._basestorage import BaseStorage

if TYPE_CHECKING:
    from ._basestorage import StorageConfig


__all__ = ("HybridStorage",)

_log = logging.getLogger(__name__)

DictLike = dict[Any, Any]

DIRTY: Literal[1] = 1
DELETED: Literal[2] = 2


class HybridStorage(BaseStorage, ABC):
    """

    .. versionadded:: 3.0
    """

    __slots__ = (
        "__flush_interval",
        "__flush_task",
        "__main_storage",
        "__cache_storage",
        "__pending_users",
        "__pending_chats",
        "__pending_flows",
        "__pending_bot",
        "__lock",
        "__is_running",
        "__semaphore",
    )

    def __init__(
        self,
        config: "StorageConfig",
        main: BaseStorage,
        cache: BaseStorage,
        flush_interval: float = 60.0,
        max_concurrency: int = 50,
    ) -> None:
        super().__init__(config)
        self.__is_running = False

        self.__main_storage: BaseStorage = main
        self.__cache_storage: BaseStorage = cache
        self.__flush_interval = flush_interval

        self.__flush_task: asyncio.Task[None] | None = None

        self.__pending_users: dict[int, Literal[1, 2]] = {}
        self.__pending_chats: dict[int, Literal[1, 2]] = {}
        self.__pending_flows: dict[str, Literal[1, 2]] = {}
        self.__pending_bot: Literal[1, 2, None] = None

        self.__lock = asyncio.Lock()
        self.__semaphore = asyncio.Semaphore(max_concurrency)

    async def __auto_flush_loop(self) -> None:
        while self.__is_running:
            try:
                await asyncio.sleep(self.__flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break

    async def flush(self) -> None:
        async with self.__lock:
            if (
                not self.__pending_users
                and not self.__pending_chats
                and not self.__pending_bot
                and not self.__pending_flows
            ):
                return

            users_to_flush = self.__pending_users
            chats_to_flush = self.__pending_chats
            flows_to_flush = self.__pending_flows
            bot_action = self.__pending_bot

            self.__pending_users = {}
            self.__pending_chats = {}
            self.__pending_flows = {}
            self.__pending_bot = None

            user_data_snapshot: dict[int, Any] = {}
            for uid, state in users_to_flush.items():
                if state == DIRTY:
                    user_data_snapshot[uid] = await self.__cache_storage.get_user_data(
                        uid
                    )

            chat_data_snapshot: dict[int, Any] = {}
            for cid, state in chats_to_flush.items():
                if state == DIRTY:
                    chat_data_snapshot[cid] = await self.__cache_storage.get_chat_data(
                        cid
                    )

            flow_data_snapshot: dict[str, Any] = {}
            for f_key, state in flows_to_flush.items():
                if state == DIRTY:
                    flow_data_snapshot[f_key] = (
                        await self.__cache_storage.get_flow_data(f_key)
                    )

            bot_data_snapshot: dict[Any, Any] | None = None
            if bot_action == DIRTY:
                bot_data_snapshot = await self.__cache_storage.get_bot_data()

        tasks = []

        for uid, state in users_to_flush.items():
            if state == DIRTY:
                tasks.append(
                    self.__safe_execute(
                        self.__main_storage.update_user_data(
                            uid, user_data_snapshot[uid]
                        )
                    )
                )
            elif state == DELETED:
                tasks.append(
                    self.__safe_execute(self.__main_storage.drop_user_data(uid))
                )

        for cid, state in chats_to_flush.items():
            if state == DIRTY:
                tasks.append(
                    self.__safe_execute(
                        self.__main_storage.update_chat_data(
                            cid, chat_data_snapshot[cid]
                        )
                    )
                )
            elif state == DELETED:
                tasks.append(
                    self.__safe_execute(self.__main_storage.drop_chat_data(cid))
                )

        for f_key, state in flows_to_flush.items():
            if state == DIRTY:
                tasks.append(
                    self.__safe_execute(
                        self.__main_storage.update_flow_data(
                            f_key, flow_data_snapshot[f_key]
                        )
                    )
                )
            elif state == DELETED:
                tasks.append(
                    self.__safe_execute(self.__main_storage.drop_flow_data(f_key))
                )

        if bot_action == DIRTY:
            tasks.append(
                self.__safe_execute(
                    self.__main_storage.update_bot_data(bot_data_snapshot)
                )
            )
        elif bot_action == DELETED:
            tasks.append(self.__safe_execute(self.__main_storage.drop_bot_data()))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def __safe_execute(self, coro: Any):
        async with self.__semaphore:
            try:
                await coro
            except Exception as exc:
                await self.__process_error(exc)

    async def __process_error(self, exc: Exception):
        _log.error("Exception occurred while flushing cache to storage", exc_info=exc)

    async def initialize(self) -> None:
        if self.__is_running:
            return
        self.__is_running = True

        await self.__main_storage.initialize()
        await self.__cache_storage.initialize()
        self.__flush_task = asyncio.create_task(
            self.__auto_flush_loop(), name="HybridStorage:auto_flush_loop"
        )
        _log.debug("HybridStorage background flush loop started.")

    async def close(self) -> None:
        if not self.__is_running:
            return

        self.__is_running = False
        if self.__flush_task:
            self.__flush_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.__flush_task

        # To avoid losing the final flush,
        # we perform one last flush after closing the loop.
        await self.flush()
        await self.__cache_storage.close()
        await self.__main_storage.close()
        _log.debug("HybridStorage stopped and flushed successfully.")

    async def get_bot_data(self) -> Any:
        async with self.__lock:
            state = self.__pending_bot

        if state == DELETED:
            return {}

        data = await self.__cache_storage.get_bot_data()
        if not data:
            data = await self.__main_storage.get_bot_data()
            if data:
                await self.__cache_storage.update_bot_data(data)

        return data

    async def update_bot_data(self, data: dict[Any, Any]) -> None:
        async with self.__lock:
            self.__pending_bot = DIRTY

        await self.__cache_storage.update_bot_data(data)

    async def drop_bot_data(self) -> None:
        async with self.__lock:
            self.__pending_bot = DELETED

        await self.__cache_storage.drop_bot_data()

    async def get_user_data(self, user_id: int) -> Any:
        async with self.__lock:
            state = self.__pending_users.get(user_id)

        if state == DELETED:
            return {}

        data = await self.__cache_storage.get_user_data(user_id)
        if not data:
            data = await self.__main_storage.get_user_data(user_id)
            if data:
                await self.__cache_storage.update_user_data(user_id, data)

        return data

    async def update_user_data(self, user_id: int, data: DictLike) -> None:
        async with self.__lock:
            self.__pending_users[user_id] = DIRTY

        await self.__cache_storage.update_user_data(user_id, data)

    async def drop_user_data(self, user_id: int) -> None:
        async with self.__lock:
            self.__pending_users[user_id] = DELETED

        await self.__cache_storage.drop_user_data(user_id)

    async def get_chat_data(self, chat_id: int) -> Any:
        async with self.__lock:
            state = self.__pending_chats.get(chat_id)

        if state == DELETED:
            return {}

        data = await self.__cache_storage.get_chat_data(chat_id)
        if not data:
            data = await self.__main_storage.get_chat_data(chat_id)
            if data:
                await self.__cache_storage.update_chat_data(chat_id, data)

        return data

    async def update_chat_data(self, chat_id: int, data: DictLike) -> None:
        async with self.__lock:
            self.__pending_chats[chat_id] = DIRTY

        await self.__cache_storage.update_chat_data(chat_id, data)

    async def drop_chat_data(self, chat_id: int) -> None:
        async with self.__lock:
            self.__pending_chats[chat_id] = DELETED

        await self.__cache_storage.drop_chat_data(chat_id)

    async def get_flow_data(self, flow_key: str) -> Any:
        async with self.__lock:
            state = self.__pending_flows.get(flow_key)

        if state == DELETED:
            return {}

        data = await self.__cache_storage.get_flow_data(flow_key)
        if not data:
            data = await self.__main_storage.get_flow_data(flow_key)
            if data:
                await self.__cache_storage.update_flow_data(flow_key, data)

        return data

    async def get_all_flow_data(self) -> dict[str, DictLike]:
        updated: list[str] = []
        deleted: list[str] = []
        async with self.__lock:
            for key, state in self.__pending_flows.items():
                (deleted if state == DELETED else updated).append(key)

        data = await self.__cache_storage.get_all_flow_data()
        if not data:
            data = await self.__main_storage.get_all_flow_data()
            for key in list(data.keys()):
                if key in deleted:
                    del data[key]

                if key in updated:
                    continue

                flow_data = data[key]
                await self.__cache_storage.update_flow_data(key, flow_data)

        return data

    async def update_flow_data(self, flow_key: str, data: DictLike) -> None:
        async with self.__lock:
            self.__pending_flows[flow_key] = DIRTY

        await self.__cache_storage.update_flow_data(flow_key, data)

    async def drop_flow_data(self, flow_key: str) -> None:
        async with self.__lock:
            self.__pending_flows[flow_key] = DELETED

        await self.__cache_storage.drop_flow_data(flow_key)
