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
from ._baleobject import BaleObject

__all__ = ("BotCommand",)


class BotCommand(BaleObject):
    """This object represents the information of a bot command in the Bale messenger.

    Equality conditions:
        1. The second object must be an instance of the :class:`BotCommand` class.
        2. The :attr:`command` attribute in both objects must be identical.

    Attributes:
        command (:obj:`str`):
            The name of the command without the leading ``/`` character. It can be a maximum of ``32`` characters and may only contain Latin letters and the ``_`` character.
        description (:obj:`str`):
            Description of the command. It can be a maximum of ``256`` characters.

    .. versionadded:: 3.0
    """

    __slots__ = (
        "command",
        "description"
    )

    def __init__(
        self,
        command: str,
        description: str
    ) -> None:
        super().__init__()
        self._id = command
        self.command = command
        self.description = description

        self._lock()
