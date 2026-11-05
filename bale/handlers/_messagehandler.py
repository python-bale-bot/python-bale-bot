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

from typing import TYPE_CHECKING

from bale.checks import Check

from ._updatehandler import UpdateHandler

if TYPE_CHECKING:
    from bale.context import Context


class MessageHandler(UpdateHandler):
    """This object shows a Message Handler.
    In this handler, only updates that show a sent message and also meet the conditions set in :paramref:`check` are covered.

    Arguments:
        check:
            The check for this handler.

            Hint:

                Called in :meth:`check_new_update`, when new update confirm. This checker indicates whether the Update should be covered by the handler or not.

    Note:
        All additional keyword arguments passed to this handler will be forwarded to the base :class:`~bale.handlers.UpdateHandler`
        via ``**kwargs``.

    .. admonition:: Input parameters for the wrapper function
        :class: seealso

        **message**: :class:`~bale.Message`
            The only parameter for this handler is the received message object.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from bale.handlers import MessageHandler

                @client.handle(MessageHandler())
                async def message_handler(message: Message):
                    return await message.reply(f'{message.author.first_name} sent {message.content}')

    .. versionadded:: 3.0
    """

    __slots__ = ("check",)

    def __init__(self, check: Check | None = None, **kwargs) -> None:
        super().__init__(**kwargs)

        if check and not isinstance(check, Check):
            raise TypeError("check param must be type of Check")

        self.check = check

    async def check_new_update(self, context: "Context") -> tuple["Context"] | None:
        update = context.update

        if update.message is not None and (
            not self.check or await self.check.check_update(context)
        ):
            return (context,)

        return None
