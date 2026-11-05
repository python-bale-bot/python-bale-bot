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

import sys
from typing import TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

__all__ = ("Chat", "ChatFullInfo")


class ChatPhoto(TypedDict, total=False):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


class Chat(TypedDict, total=False):
    id: int
    type: str
    title: NotRequired[str | None]
    first_name: NotRequired[str | None]
    last_name: NotRequired[str | None]
    username: NotRequired[str | None]


class ChatFullInfo(TypedDict, total=False):
    id: int
    type: str
    title: NotRequired[str | None]
    first_name: NotRequired[str | None]
    last_name: NotRequired[str | None]
    username: NotRequired[str | None]
    photo: NotRequired[ChatPhoto | None]
    description: NotRequired[str | None]
    invite_link: NotRequired[str | None]
    linked_chat_id: NotRequired[str | None]
