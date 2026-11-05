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
from ._baleobject import BaleObject

__all__ = ("MessageEntity",)


class MessageEntity(BaleObject):
    """This object represents a specific part of a text message sent in the `Bale <https://ble.ir>`_ messenger. Currently, only mentioned usernames (``@mention``) and commands (``/start``) are supported.

    Hint:
        In the Telegram messenger—which Bale's bot web service closely follows—texts are received entirely raw. In other words, expressions like **bold** and ``[link](url)`` are not seen in properties such as :attr:`Message.text`. However, it provides objects called Entities along with the raw text, the advantage of which is preventing complexities related to processing structures like markdown or html.
        Therefore, it has little use for developers in `Bale <https://ble.ir>`_.

    Equality conditions:
        1. The second object must be an instance of :class:`MessageEntity`.
        2. All attributes of both classes must be identical (:attr:`type`, :attr:`offset` & :attr:`length`).

    Attributes:
        type (:obj:`str`):
            Type of the message entity. Currently, supports either ``mention`` or ``bot_command``.
        offset (:obj:`int`):
            Offset for the start of the entity in the message in ``UTF-16`` code units.
        length (:obj:`int`):
            Length of the entity in the message in ``UTF-16`` code units.

    Note:
         In Python, Unicode (or ``UTF-8``) characters are used by default. However, Telegram and Bale servers use ``UTF-16``. The difference between the two in characters like emojis (🤗) is that they are considered as **one** unit in ``UTF-8`` and **two** units in ``UTF-16``.

    .. versionadded:: 3.0
    """

    __slots__ = ("type", "offset", "length")

    def __init__(self, type: str, offset: int, length: int) -> None:
        super().__init__()
        self._id = (type, offset, length)
        self.type = type
        self.offset = offset
        self.length = length

    def __hash__(self) -> int:
        """:meta private:"""
        return hash(self._id)
