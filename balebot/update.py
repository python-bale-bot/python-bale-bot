from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balebot import Bot, CallbackQuery, Message, User, Components

class Update():
    __slots__ = (
        "id",
        "type",        
        "message",        
        "callback_query",   
        "edited_message",    
        "bot"
    )
    def __init__(self, id : int, callback_query : CallbackQuery = None, message : Message = None, edited_message : Message = None, bot : 'Bot' = None):
        self.id = int(id)
        self.bot = bot
        self.callback_query = None
        self.message = None
        self.edited_message = None
        if callback_query:
            self.callback_query = callback_query
            self.message : Message = self.callback_query.message
        elif message:
            self.message = message
        elif edited_message:
            self.edited_message = message
            
    @property
    def type(self):
        if self.callback_query:
            return "callback_query"
        elif self.message:
            return "message"
        return "unknown"
    
    @classmethod
    def dict(cls, data : dict, bot):
        callback_query = None
        message = None
        edited_message = None
        if data.get("callback_query"):
            callback_query = CallbackQuery.dict(data.get("callback_query"), bot = bot)
            message = callback_query.message
        elif data.get("message"):
            message = Message.dict(data.get("message"), bot = bot)
        elif data.get("edited_message"):
            edited_message = Message.dict(data = data.get("edited_message"), bot = bot)

        return cls(id = data["update_id"], message = message, callback_query = callback_query, edited_message = edited_message)
    
    def to_dict(self):
        data = {}
        
        data["callback_query"] = self.callback_query if self.callback_query.to_dict() is not None else None
        data["message"] = self.message if self.message.to_dict() is not None else None
        data["edited_message"] = self.edited_message if self.edited_message.to_dict() is not None else None
        data["type"] = self.type
        
        return data