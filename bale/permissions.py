"""
MIT License

Copyright (c) 2023 Kian Ahmadian

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
class Permissions:
    """This object shows the permissions and permissions of an admin or a member in a group (or channel).

        Args:
            can_be_edited (bool): Can you edit?. Defaults to False.
            can_change_info (bool): Can you edit group information? Defaults to False.
            can_post_messages (bool): Can he post a message?. Defaults to False.
            can_edit_messages (bool): Can you edit your message? Defaults to False.
            can_delete_messages (bool): Can it erase messages? Defaults to False.
            can_invite_users (bool): Can it invite users to chat? Defaults to False.
            can_restrict_members (bool): Defaults to False.
            can_pin_messages (bool): Can you pin your message? Defaults to False.
            can_promote_members (bool): Defaults to False.
            can_send_messages (bool): Can he send a message?. Defaults to False.
            can_send_media_messages (bool): Can it attach a file with the message? Defaults to False.
    """
    __slots__ = (
        "can_be_edited",
        "can_change_info",
        "can_post_messages",
        "can_edit_messages",
        "can_delete_messages",
        "can_invite_users",
        "can_restrict_members",
        "can_pin_messages",
        "can_promote_members",
        "can_send_messages",
        "can_send_media_messages"
    )

    def __init__(self, can_be_edited: bool = False, can_change_info: bool = False, can_post_messages: bool = False,
                 can_edit_messages: bool = False, can_delete_messages: bool = False, can_invite_users: bool = False,
                 can_restrict_members: bool = False, can_pin_messages: bool = False, can_promote_members: bool = False,
                 can_send_messages: bool = False, can_send_media_messages: bool = False):
        self.can_be_edited = can_be_edited
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

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        return cls(can_be_edited=data.get("can_be_edited", False), can_change_info=data.get("can_change_info", False),
                   can_post_messages=data.get("can_post_messages", False), can_edit_messages=data.get("can_edit_messages", False),
                   can_delete_messages=data.get("can_delete_messages", False), can_invite_users=data.get("can_invite_users", False),
                   can_restrict_members=data.get("can_restrict_members", False), can_pin_messages=data.get("can_pin_messages", False),
                   can_promote_members=data.get("can_promote_members", False), can_send_messages=data.get("can_send_messages", False),
                   can_send_media_messages=data.get("can_send_media_messages", False))
