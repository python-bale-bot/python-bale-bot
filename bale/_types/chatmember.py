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

import sys
from typing import TYPE_CHECKING, Literal, TypedDict

if sys.version_info >= (3, 11):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .user import User

__all__ = ("ChatMember",)


class ChatMemberOwner(TypedDict):
    status: Literal["creator"]
    user: "User"
    is_anonymous: NotRequired[bool | None]
    custom_title: NotRequired[str | None]


class ChatMemberAdministrator(TypedDict):
    status: Literal["administrator"]
    user: "User"
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_stories: bool
    can_post_messages: NotRequired[bool | None]
    can_edit_messages: NotRequired[bool | None]
    can_pin_messages: NotRequired[bool | None]
    is_anonymous: NotRequired[bool | None]
    can_manage_chat: NotRequired[bool | None]
    custom_title: NotRequired[str | None]


class ChatMemberMember(TypedDict):
    status: Literal["member"]
    user: "User"
    until_date: NotRequired[int]


class ChatMemberRestricted(TypedDict):
    status: Literal["restricted"]
    user: "User"
    is_member: bool
    can_send_messages: bool
    can_send_audios: bool
    can_send_documents: bool
    can_send_photos: bool
    can_send_videos: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    until_date: int
    can_send_video_notes: NotRequired[bool | None]
    can_send_voice_notes: NotRequired[bool | None]
    can_send_polls: NotRequired[bool | None]
    can_send_other_messages: NotRequired[bool | None]
    can_add_web_page_previews: NotRequired[bool | None]


ChatMember = (
    ChatMemberOwner | ChatMemberAdministrator | ChatMemberMember | ChatMemberRestricted
)
