from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balebot import Bot

from balebot import Components

class User():
    __slots__ = (
        "first_name", 
        "last_name",
        "username",
        "id",
        "bot"
    )
    def __init__(self, id : int, first_name : str, last_name : str = None, username : str = None, bot : 'Bot' = None):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.id = str(id)
        self.bot = bot
        
    @property
    def link(self):
        if self.username:
            return "https://ble.ir/@{username}".format(username = self.username)
        return None

    def send(self, text, components : Components = None, reply_to_message_id : str = None):
        json = {}
        json["chat_id"] = self.id
        json["text"] = text
        if components:
            json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.bot.send_message(chat_id = self.id, text = text, components = components, timeout = (10, 15)) 
        return message
    
    def __str__(self):
        return (str(self.username) + " #" + str(self.id) if self.username else str(self.first_name) + " " + str(self.last_name))
    
    @classmethod
    def dict(cls, bot, data : dict):
        return cls(username = data["username"], first_name = data["first_name"], last_name = data["last_name"], id = data["id"], bot = bot)
    
    def to_dict(self):
        data = {}
        
        data["first_name"] = self.first_name if self.first_name is not None else None
        data["last_name"] = self.last_name if self.last_name is not None else None
        data["username"] = self.username if self.username is not None else None
        data["id"] = self.id if self.id is not None else None
        
        return data
    