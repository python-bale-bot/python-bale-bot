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
from __future__ import annotations

from typing import Coroutine, Callable, Tuple, Optional, TYPE_CHECKING

from bale.utils.types import UT

if TYPE_CHECKING:
    from bale import Update

__all__ = (
    "BaseHandler",
)


class BaseHandler:
    """This object shows a Base Handler.
    This is a base class for all update handlers. You can create custom handlers by inheriting from it.
    TODO: COMPLETE DOCSTRING
    """
    __slots__ = ("_callback",)

    def __init__(self):
        self._callback: Optional[Callable[[UT], Coroutine[...]]] = None

    @property
    def callback(self) -> Optional[Callable[[UT], Coroutine[...]]]:
        return self._callback

    @callback.setter
    def callback(self, _):
        raise ValueError(
            # TODO: MUST BE COMPLETE
            "You can't set callback "
        )

    def set_callback(self, callback: Callable[[UT, ...], Coroutine[...]]):
        """Register new handler callback.
        It will be called during the new Update process after confirming the :meth:`check_new_update` function.

        Parameters
        ----------
            callback: Callable[[UT, ...], Coroutine[...]]
                The new callback function.
        """
        self._callback = callback

    def check_new_update(self, update: "Update") -> Optional[Tuple]:
        """This function determines whether the "update" should be covered by the handler or not.

        Parameters
        ----------
            update: :class:`bale.Update`
                The update to be tested.

        Returns
        -------
            If :obj:`False` or :obj:`None` is returned, the update should not be wrapped by the handler,
            otherwise the handler is required to wrapp that update.
        """


    async def handle_update(self, update: "Update", *args):
        """This function works if the handler is required to cover the new Update and calls the :attr:`callback` function.

        Parameters
        ----------
            update: :class:`bale.Update`
                The update to be tested.
            args:
                Additional objects, if given to this parameter, will be passed directly to the :attr:`callback` function.
        """
        if self.callback:
            if self is BaseHandler:
                return await self.callback(update)
            return await self.callback(*args)
