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
from .._baleobject import BaleObject

__all__ = ("CopyTextButton",)


class CopyTextButton(BaleObject):
    """This object shows a copy text button.

    This object represents an inline button that copies the specified text.

    Attributes:
        text (:obj:`str`):
            The text that is copied when the button is pressed; between ``1``-``256`` characters are accepted.

    .. versionadded:: 3.0
    """

    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

        self._lock()
