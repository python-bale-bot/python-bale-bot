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

from abc import ABC
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from ._basestorage import BaseStorage

if TYPE_CHECKING:
    from ._basestorage import StorageConfig

__all__ = ("MemoryStorage",)

DictLike = dict[Any, Any]


class MemoryStorage(BaseStorage, ABC):
    """

    .. versionadded:: 3.0
    """

    __slots__ = ("_bot_data", "_user_data", "_chat_data", "_flow_data")

    def __init__(
        self,
        config: "StorageConfig",
        bot_data: dict[Any, Any] | None = None,
        user_data: dict[int, Any] | None = None,
        chat_data: dict[int, Any] | None = None,
        flow_data: dict[str, Any] | None = None,
    ):
        super().__init__(config)
        if bot_data is None:
            bot_data = {}
        if user_data is None:
            user_data = {}
        if chat_data is None:
            chat_data = {}
        if flow_data is None:
            flow_data = {}

        self._bot_data: dict[Any, Any] = bot_data
        self._user_data: dict[int, Any] = user_data
        self._chat_data: dict[int, Any] = chat_data
        self._flow_data: dict[str, Any] = flow_data

    @property
    def bot_data(self) -> dict[Any, Any]:
        return self._bot_data

    @property
    def user_data(self) -> dict[int, Any]:
        return self._user_data

    @property
    def chat_data(self) -> dict[int, Any]:
        return self._chat_data

    @property
    def flow_data(self) -> dict[str, Any]:
        return self._flow_data

    async def update_bot_data(self, data: dict[str, Any]) -> None:
        if self.bot_data != data:
            self._bot_data = data

    async def update_chat_data(self, chat_id: int, data: dict[Any, Any]) -> None:
        if self.chat_data.get(chat_id) != data:
            self._chat_data[chat_id] = data

    async def update_user_data(self, user_id: int, data: dict[Any, Any]) -> None:
        if self.user_data.get(user_id) != data:
            self._user_data[user_id] = data

    async def update_flow_data(self, flow_key: str, data: dict[Any, Any]) -> None:
        if self._flow_data.get(flow_key) != data:
            self._flow_data[flow_key] = data

    async def get_bot_data(self) -> Any:
        return deepcopy(self._bot_data)

    async def get_user_data(self, user_id: int) -> Any:
        return deepcopy(self._user_data.get(user_id, {}))

    async def get_chat_data(self, chat_id: int) -> Any:
        return deepcopy(self._chat_data.get(chat_id, {}))

    async def get_flow_data(self, flow_key: str) -> Any:
        return deepcopy(self._flow_data[flow_key])

    async def get_all_flow_data(self) -> dict[str, DictLike]:
        return deepcopy(self._flow_data)

    async def drop_chat_data(self, chat_id: int) -> None:
        if chat_id in self._chat_data:
            del self._chat_data[chat_id]

    async def drop_user_data(self, user_id: int) -> None:
        if user_id not in self._user_data:
            del self._user_data[user_id]

    async def drop_bot_data(self) -> None:
        await self.update_bot_data({})

    async def drop_flow_data(self, flow_key: str) -> None:
        if flow_key in self._flow_data:
            del self._flow_data[flow_key]

    async def initialize(self) -> None:
        pass

    async def close(self) -> None:
        pass
