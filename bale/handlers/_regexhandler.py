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

import re
from typing import TYPE_CHECKING, Pattern

from ._updatehandler import UpdateHandler

if TYPE_CHECKING:
    from bale.context import Context


class RegexHandler(UpdateHandler):
    r"""This object shows a Regex Handler.
    In this handler, only updates that show a sent message and whose message text matches the pattern set in :paramref:`pattern` are covered.

    Arguments:
        pattern:
            The regular expression pattern used to match the incoming message text.
            If a string is provided, it will be compiled into a regex pattern using :func:`re.compile`.


    Note:
        All additional keyword arguments passed to this handler will be forwarded to the base :class:`~bale.handlers.UpdateHandler`
        via ``**kwargs``.

    .. admonition:: Input parameters for the wrapper function
        :class: seealso

        **message**: :class:`~bale.Message`
            The first parameter for this handler is the received message object.
        **match**: :class:`~typing.Match`
            In this parameter, the result of the match found between the sent message text and the existing pattern, which has been checked by the :func:`re.match` function, is placed.

        .. admonition:: Example Code
            :class: tip

            .. code-block:: python

                from typing import Match
                from bale.handlers import RegexHandler

                @client.handle(RegexHandler(r'^salam,?\s*(\S+)'))
                async def regex_handler(message: bale.Message, match: Match):
                    return await callback.message.chat.send(f'{message.author.mention} say hello to {match.group(1)}')

    .. versionadded:: 3.0
    """

    __slots__ = ("pattern",)

    def __init__(self, pattern: str | Pattern[str], **kwargs) -> None:
        super().__init__(**kwargs)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern: Pattern[str] = pattern

    async def check_new_update(self, context: "Context"):  # type: ignore[override]
        update = context.update

        if update.message is not None and (
            update.message.text and (match := self.pattern.match(update.message.text))
        ):
            return context, match

        return None
