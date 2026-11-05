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

if TYPE_CHECKING:
    from bale import MessageEntity


def extract_entity_text(
    text: str,
    offset: int | None = None,
    length: int | None = None,
    entity: "MessageEntity | None" = None,
):
    if entity:
        offset, length = entity.offset, entity.length
    if offset is None or length is None:
        raise ValueError(
            "Either 'entity' or both 'offset' and 'length' must be provided."
        )

    return text.encode("utf-16-le")[offset * 2 : (offset + length) * 2].decode(
        "utf-16-le"
    )
