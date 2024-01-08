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
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
    from bale import Bot

from bale import BaleObject, User

__all__ = (
    "ChatMember",
)

class ChatMember(BaleObject):
    """This object shows a member in chat.

    Attributes
    ----------
        user: :class:`bale.User`
            Information about the chat member.
        status: :class:`str`
            The member’s status in the chat.
        can_be_edited: :class:`bool`
                :obj:`True`, if the bot is allowed to edit administrator privileges of that user.
        can_change_info: :class:`bool`
            :obj:`True`, if the user can change the chat title, photo and other settings.
        can_post_messages: :class:`bool`
            :obj:`True`, if the administrator can post messages in the channel,
            or access channel statistics; channels only.
        can_edit_messages: :class:`bool`
            :obj:`True`,
            if the administrator can edit messages of other users and can pin messages; channels only.
        can_delete_messages: :class:`bool`
            :obj:`True`, if the administrator can delete messages of other users.
        can_invite_users: :class:`bool`
            :obj:`True`, if the user can invite new users to the chat.
        can_restrict_members: :class:`bool`
            :obj:`True`, if the administrator can restrict, ban or unban chat members.
        can_pin_messages: :class:`bool`
            :obj:`True`, if the user is allowed to pin messages, groups, channels only.
        can_promote_members: :class:`bool`
            :obj:`True`,
            if the administrator can add new administrators with a subset of his own privileges or demote administrators
            that he has promoted, directly or indirectly (promoted by administrators that were appointed by the user).
        can_send_messages: :class:`bool`
            :obj:`True`, if the user is allowed to send messages.
        can_send_media_messages: :class:`bool`
            :obj:`True`, if the user is allowed to send a media message.
        can_reply_to_story: :class:`bool`
            :obj:`True`, if the user is allowed to reply to a story.
        can_send_link_message: :class:`bool`
            :obj:`True`, if the user is allowed to send a link message.
        can_send_forwarded_message: :class:`bool`
            :obj:`True`, if the user is allowed to forward a message to chat.
        can_see_members: :class:`bool`
            :obj:`True`, if the user is allowed to see the list of chat members.
        can_add_story: :class:`bool`
            :obj:`True`, if the user is allowed to post a story from chat.
    """
    OWNER = "creator"
    ADMIN = "administrator"
    MEMBER = "member"
    __slots__ = (
        "user",
        "status",
        "is_member",
        "can_change_info",
        "can_post_messages",
        "can_edit_messages",
        "can_delete_messages",
        "can_invite_users",
        "can_restrict_members",
        "can_pin_messages",
        "can_promote_members",
        "can_send_messages",
        "can_send_media_messages",
        "can_reply_to_story",
        "can_send_link_message",
        "can_send_forwarded_message",
        "can_see_members",
        "can_add_story",
        "can_be_edited"
    )

    def __init__(
            self, status: str, user: "User", is_member: Optional[bool],
            can_change_info: Optional[bool], can_post_messages: Optional[bool],
            can_edit_messages: Optional[bool], can_delete_messages: Optional[bool],
            can_invite_users: Optional[bool], can_restrict_members: Optional[bool],
            can_pin_messages: Optional[bool], can_promote_members: Optional[bool],
            can_send_messages: Optional[bool], can_send_media_messages: Optional[bool],
            can_reply_to_story: Optional[bool], can_send_link_message: Optional[bool],
            can_send_forwarded_message: Optional[bool], can_see_members: Optional[bool],
            can_add_story: Optional[bool], can_be_edited: Optional[bool]
    ):
        super().__init__()
        self.status = status
        self.user = user
        self.is_member = is_member
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_post_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_reply_to_story = can_reply_to_story
        self.can_send_link_message = can_send_link_message
        self.can_send_forwarded_message = can_send_forwarded_message
        self.can_see_members = can_see_members
        self.can_add_story = can_add_story
        self.can_be_edited = can_be_edited
        self._id = (self.user, self.status)

        self._lock()

    @property
    def is_owner(self) -> bool:
        return self.status == self.OWNER

    @property
    def is_admin(self) -> bool:
        return self.status in (self.OWNER, self.ADMIN)

    @classmethod
    def from_dict(cls, data: Optional[Dict], bot: "Bot"):
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data['user'] = User.from_dict(data.get('user'), bot)

        return super().from_dict(data, bot)
