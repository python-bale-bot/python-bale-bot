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
from bale import BaleObject

__all__ = (
    "WebhookInfo",
)


class WebhookInfo(BaleObject):
    """This object shows a WebhookInfo.

    Attributes
    ----------
        url: :obj:`str`
            Webhook URL, may be empty if webhook is not set up.
        has_custom_certificate: :obj:`bool`
            :obj:`True`, if a custom certificate was provided for webhook certificate checks.
        pending_update_count: :obj:`int`
            Number of updates awaiting delivery.
    """
    __slots__ = (
        "url",
        "has_custom_certificate",
        "pending_update_count"
    )

    def __init__(self, url: str, has_custom_certificate: int, pending_update_count: int) -> None:
        super().__init__()
        self.url = url
        self.has_custom_certificate = has_custom_certificate
        self.pending_update_count = pending_update_count
