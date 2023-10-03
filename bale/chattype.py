__all__ = (
    'ChatType',
)

class ChatType:
    """This object represents a chat type.
    By using this class, you can easily check the process of comparing and reviewing several types of chats.

    Parameters
    ----------
        value: :class:`str`
            The type of Chat.

    """
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"

    __slots__ = (
        "value",
    )

    def __init__(self, value: str):
        self.value = value

    @property
    def is_private_chat(self):
        """:class:`bool`: Return ``True`` if Chat is a Private"""
        return self.value == self.PRIVATE

    @property
    def is_group_chat(self):
        """:class:`bool`: Return ``True`` if Chat is a Group"""
        return self.value == self.GROUP

    @property
    def is_channel_chat(self):
        """:class:`bool`: Return ``True`` if Chat is a Channel"""
        return self.value == self.CHANNEL

    def __eq__(self, other):
        return isinstance(other, ChatType) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)