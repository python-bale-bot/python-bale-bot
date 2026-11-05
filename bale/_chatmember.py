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

from ._baleobject import BaleObject
from ._user import User
from .constants import ChatMemberStatus

if TYPE_CHECKING:
    from bale import Bot

    from ._types.chatmember import ChatMember as ChatMemberPayload


__all__ = ("ChatMember",)


class ChatMember(BaleObject):
    """This object shows a member in chat.

    Attributes:
        user (:class:`~bale.User`):
            Information about the chat member.
        status (:obj:`str`):
            The member’s status in the chat.
        can_be_edited (:obj:`bool`, optional):
                :obj:`True`, if the bot is allowed to edit administrator privileges of that user.
        can_change_info (:obj:`bool`, optional):
            :obj:`True`, if the user can change the chat title, photo and other settings.
        can_post_messages (:obj:`bool`, optional):
            :obj:`True`, if the administrator can post messages in the channel,
            or access channel statistics; channels only.
        can_edit_messages (:obj:`bool`, optional):
            :obj:`True`,
            if the administrator can edit messages of other users and can pin messages; channels only.
        can_delete_messages (:obj:`bool`, optional):
            :obj:`True`, if the administrator can delete messages of other users.
        can_invite_users (:obj:`bool`, optional):
            :obj:`True`, if the user can invite new users to the chat.
        can_restrict_members (:obj:`bool`, optional):
            :obj:`True`, if the administrator can restrict, ban or unban chat members.
        can_pin_messages (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to pin messages, groups, channels only.
        can_promote_members (:obj:`bool`, optional):
            :obj:`True`,
            if the administrator can add new administrators with a subset of his own privileges or demote administrators
            that he has promoted, directly or indirectly (promoted by administrators that were appointed by the user).
        can_send_messages (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to send messages.
        can_send_media_messages (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to send a media message.
        can_reply_to_story (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to reply to a story.
        can_send_link_message (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to send a link message.
        can_send_forwarded_message (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to forward a message to chat.
        can_see_members (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to see the list of chat members.
        can_add_story (:obj:`bool`, optional):
            :obj:`True`, if the user is allowed to post a story from chat.
    """

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
        "can_be_edited",
    )

    def __init__(
        self,
        status: str,
        user: "User | None" = None,
        is_member: bool | None = None,
        can_change_info: bool | None = None,
        can_post_messages: bool | None = None,
        can_edit_messages: bool | None = None,
        can_delete_messages: bool | None = None,
        can_invite_users: bool | None = None,
        can_restrict_members: bool | None = None,
        can_pin_messages: bool | None = None,
        can_promote_members: bool | None = None,
        can_send_messages: bool | None = None,
        can_send_media_messages: bool | None = None,
        can_reply_to_story: bool | None = None,
        can_send_link_message: bool | None = None,
        can_send_forwarded_message: bool | None = None,
        can_see_members: bool | None = None,
        can_add_story: bool | None = None,
        can_be_edited: bool | None = None,
    ) -> None:
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
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        self.can_reply_to_story = can_reply_to_story
        self.can_send_link_message = can_send_link_message
        self.can_send_forwarded_message = can_send_forwarded_message
        self.can_see_members = can_see_members
        self.can_add_story = can_add_story
        self.can_be_edited = can_be_edited

        self._lock()

    @property
    def is_creator(self) -> bool:
        """
        This property checks if the :attr:`status` attribute of the instance
        is equal to the ``OWNER`` constant.

        Returns:
             :obj:`True` if the status is equal to ``creator``, :obj:`False` otherwise.
        """
        return self.status == ChatMemberStatus.CREATOR

    @property
    def is_admin(self) -> bool:
        """
        This property checks if the :attr:`status` attribute of the instance
        is equal to the ``ADMIN`` or ``OWNER`` constant.

        Returns:
             :obj:`True` if the status is equal to ``creator`` or ``administrator``, :obj:`False` otherwise.
        """
        return self.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMIN)

    @classmethod
    def from_dict(
        cls, data: "ChatMemberPayload | None" = None, bot: "Bot | None" = None
    ):
        """:meta private:"""
        data = BaleObject.parse_data(data)
        if not data:
            return None

        data["user"] = User.from_dict(data.get("user"), bot)

        return super().from_dict(data, bot)
