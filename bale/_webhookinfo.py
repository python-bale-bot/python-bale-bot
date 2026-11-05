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

__all__ = ("WebhookInfo",)


class WebhookInfo(BaleObject):
    """This object represents information about the webhook status.

    Equality conditions:
        1. The second object must be an instance of the :class:`WebhookInfo` class.
        2. Both must have the same :attr:`url`.

    Attributes:
        url (:obj:`str`):
            Webhook address. If the webhook is not set, this value may be empty.
        pending_update_count (:obj:`int`):
            Number of updates awaiting delivery.

    .. versionadded:: 3.0
    """

    __slots__ = ("url", "has_custom_certificate", "pending_update_count")

    def __init__(self, url: str, pending_update_count: int) -> None:
        super().__init__()
        self.url = url
        self.pending_update_count = pending_update_count

        self._lock()
