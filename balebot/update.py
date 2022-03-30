from .user  import User
from .components import ReplyMarkup
from .message import Message

class Update():
    __slots__ = (
        "id",
        "type",        
        "message",        
        "callback_query",   
        "edited_message",    
        "bot"
    )
    def __init__(self, id : int, callback_query = None, message = None, edited_message = None, bot = None):
        self.id = int(id)
        self.bot = bot
        if callback_query:
            self.callback_query = CallbackQuery(update.get("callback_query"), self)
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
            message = message
        elif data.get("edited_message"):
            edited_message = Message.dict(data = data.get("edited_message"), bot = bot )

        return cls(id = data["update_id"], message = message, callback_query = callback_query, edited_message = edited_message)