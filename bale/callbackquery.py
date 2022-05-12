from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot
    
from bale import User, Message

class CallbackQuery():
    __slots__ = (
        "message",
        "inline_message_id",
        "from_user",
        "data",
        "bot",
        "id"
    )
    def __init__(self, id : int, data : str, message : "Message", inline_message_id : str, from_user : "User", bot : "Bot" = None):
        self.data = data
        self.id = id
        self.message = message
        self.inline_message_id = inline_message_id
        self.from_user = from_user
        self.bot = bot
    
    @classmethod
    def fron_dict(cls, data : dict, bot):
        return cls(bot = bot, data = data["data"], id = data["id"], message = Message.from_dict(data["message"], bot = bot), inline_message_id = data["inline_message_id"], from_user = User.from_dict(bot = bot, data = data["from"])) 
        
    def to_dict(self):
        data = {}
        
        data["id"] = self.id
        data["data"] = self.data
        data["inline_message_id"] = self.inline_message_id
        data["message"] = self.message.to_dict()
        data["from_user"] = self.from_user.to_dict()
        
        return data