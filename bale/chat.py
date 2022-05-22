from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot, Message

class Chat():
    PRIVATE = "private"
    GROUP = "group"
    
    __slots__ = (
        "id",
        "type",
        "title",
        "username",
        "first_name",
        "last_name",
        "pinned_messages",
        "all_members_are_administrators",
        "bot"
    )
    def __init__(self, id : str, type : str, title : str, username : str, first_name : str, last_name : str, pinned_messages : list["Message"] = [], all_members_are_administrators : bool = True, bot : 'Bot' = None):
        """This object indicates a chat.

        Args:
            id (str): Chat ID.
            type (str): Chat Type.
            title (str): Chat Title.
            username (str): Chat Username (for DM or PV).
            first_name (str): First name Chat (for DM or PV).
            last_name (str): Last name Chat (for DM or PV).
            pinned_messages (list[:class:`bale.Message`]): Pinned messages in chat. Defaults to [].
            all_members_are_administrators (bool): Does everyone have admin access?. Defaults to True. (for Group)
            bot (bale.Bot): Bot Object. Defaults to None.
        """
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_messages = pinned_messages
        self.all_members_are_administrators = all_members_are_administrators
        self.bot = bot
     
    def send(self, text : str, components = None, timeout = (5, 10)):
        """:meth:`telegram.Bot.send_message`.

        Args:
            text (str): Message Text.
            components (:class:`bale.Components`, dict): Defaults to None.
            timeout (tuple, int): Defaults to (5, 10).
        Returns:
            List(:class:`bale.Message`)
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        message = self.bot.send_message(chat_id = str(self.id), text = text, components = components, timeout = timeout)
        return message
        
    def chat_administrators(self, timeout = (10, 30)):
        """:meth:`telegram.Bot.get_chat_administrators`.

        Args:
            timeout (tuple, optional): _description_. Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Returns:
            List[:class:`bale.ChatMember`]
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        administrators = self.bot.get_chat_administrators(self.id, timeout = timeout)
        return administrators
        
    @classmethod
    def from_dict(cls, data : dict, bot):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        pinned_messages = []
        if data.get("pinned_message") and isinstance(data["pinned_message"], list):
            for i in data["pinned_message"]:
                pinned_messages.append(Message.from_dict(bot = bot, data = i))
        return cls(bot = bot, id = data.get("id"), type = data.get("type"), title = data.get("title"), username = data.get("username"), first_name = data.get("first_name"), last_name = data.get("last_name"), pinned_messages = pinned_messages, all_members_are_administrators = data.get("all_members_are_administrators", True))
     
    def to_dict(self):
        data = {}
        pinned_messages = []
        
        if isinstance(data["pinned_message"], list):
            for i in data["pinned_message"]:
                if isinstance(i, Message):
                    pinned_messages.append(i.to_dict())
                else:
                    pinned_messages.append(i)   
                    
        data["id"] = self.id
        data["type"] = self.type
        data["title"] = self.title
        data["username"] = self.username
        data["first_name"] = self.first_name
        data["last_name"] = self.last_name
        data["pinned_message"] = pinned_messages
    
        return data
        