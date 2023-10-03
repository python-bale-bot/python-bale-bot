__all__ = (
    "ChatMemberStatus",
)

class ChatMemberStatus:
    """This object shows the status of the chat member.
    Using this class, you can check the process of comparing and reviewing chat members more easily.

    Parameters
    ----------
        value: :class:`str`
            The status of Chat Member.

    """
    OWNER = "creator"
    ADMIN = "administrator"
    MEMBER = "member"
    __slots__ = (
        "value",
    )

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def is_owner(self):
        """:class:`bool`: Return ``True`` if Member is chat creator"""
        return self.value == self.OWNER

    def is_admin(self):
        """:class:`bool`: Return ``True`` if Member have admin status"""
        return self.value == self.ADMIN

    def is_member(self):
        """:class:`bool`: Return ``True`` if Member haven't any status"""
        return self.value == self.MEMBER

    def __eq__(self, other):
        return isinstance(other, ChatMemberStatus) and self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)