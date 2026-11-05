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
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.

from __future__ import annotations

__all__ = ("ContextData", "ContextDataScope")

from typing import TYPE_CHECKING, Any

from .._utils.constants import ContextDataScope

if TYPE_CHECKING:
    from bale.storage import BaseStorage


class ContextData:
    """

    .. versionadded:: 3.0
    """

    __slots__ = ("_storage", "_scope", "_key")

    def __init__(
        self, storage: "BaseStorage", scope: ContextDataScope, key: int | None = None
    ) -> None:
        self._storage = storage
        self._scope: ContextDataScope = scope
        self._key = key

    async def get_raw(self) -> dict[str, Any]:
        if self._scope is ContextDataScope.BOT:
            return await self._storage.get_bot_data()
        if self._scope is ContextDataScope.CHAT and self._key is not None:
            return await self._storage.get_chat_data(self._key)
        if self._scope is ContextDataScope.USER and self._key is not None:
            return await self._storage.get_user_data(self._key)

        return {}

    async def update_raw(self, data: dict[str, Any]) -> None:
        if self._scope is ContextDataScope.BOT:
            return await self._storage.update_bot_data(data)
        if self._scope is ContextDataScope.CHAT and self._key is not None:
            return await self._storage.update_chat_data(self._key, data)
        if self._scope is ContextDataScope.USER and self._key is not None:
            return await self._storage.update_user_data(self._key, data)
        return None

    async def clear_raw(self) -> None:
        if self._scope is ContextDataScope.BOT:
            return await self._storage.drop_bot_data()
        elif self._scope is ContextDataScope.CHAT and self._key is not None:
            return await self._storage.drop_chat_data(self._key)
        elif self._scope is ContextDataScope.USER and self._key is not None:
            return await self._storage.drop_user_data(self._key)
        return None

    async def get(self, field: str, default: Any = None) -> Any:
        return (await self.get_raw()).get(field, default)

    async def set(self, field: str, value: Any) -> None:
        data = await self.get_raw()
        data[field] = value
        await self.update_raw(data)

    async def update(self, **kwargs) -> None:
        data = await self.get_raw()
        data.update(**kwargs)
        await self.update_raw(data)

    async def remove(self, field: str) -> Any:
        data = await self.get_raw()
        data.pop(field, None)
        await self.update_raw(data)

    async def clear(self) -> None:
        await self.clear_raw()
