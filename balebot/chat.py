from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balebot import Bot, Message

from balebot import Components

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
        "pinned_message",
        "bot"
    )
    def __init__(self, id : str, type : str, title : str, username : str, first_name : str, last_name : str, pinned_message : list["Message"] = [], all_members_are_administrators : bool = True, bot : 'Bot' = None):
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pinned_message = pinned_message
        self.bot = bot
     
    def send(self, text : str = None,
        sticker = None, files = None, components = None, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        message = self.bot.send_message(chat_id = str(self.id), text = text, components = components, timeout = timeout)
        return message
        
    @classmethod
    def dict(cls, data : dict, bot):
        pinned_message = []
        if isinstance(data["pinned_message"], list):
            for i in data["pinned_message"]:
                pinned_message.append(Message.dict(bot = bot, data = i))
        return cls(bot = bot, id = data.get("id"), type = data.get("type"), title = data.get("title"), username = data.get("username"), first_name = data.get("first_name"), last_name = data.get("last_name"), pinned_message = pinned_message, all_members_are_administrators = data.get("all_members_are_administrators", True))
     
    def to_dict(self):
        data = {}
        
        pinned_message = []
        if isinstance(data["pinned_message"], list):
            for i in data["pinned_message"]:
                if isinstance(i, Message):
                    pinned_message.append(i.to_dict())
                else:
                    pinned_message.append(i)   
        data["id"] = self.id
        data["type"] = self.type
        data["title"] = self.title
        data["username"] = self.username
        data["first_name"] = self.first_name
        data["last_name"] = self.last_name
        data["pinned_message"] = pinned_message
    
        return data
        