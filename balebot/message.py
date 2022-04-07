import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balebot import Bot
   
from balebot import (Chat, User, Components, Audio, ContactMessage, Location)
    
class Message():
    __slots__ = (
        "text", "caption", "from_user", "_author","contact", "chat","message_id", "date_code", "date", "edit_date", "audio", "document", "photo", "voice", "location", "invoice", "new_chat_members", "bot"
    )
    def __init__(self, message_id : str, date : datetime.datetime, text = None, caption : str = None, from_user : "User" = None, contact : "ContactMessage" = None, chat : "Chat" = None, document = None, photo = None, voice : "Audio" = None, location : "Location" = None, invoice = None, new_chat_members : list["User"] = None,bot : 'Bot' = None):
        self.message_id = message_id if message_id is not None else None
        self.date = date if date is not None else None
        
        self.text = text if text is not None else None
        self.chat = chat if chat is not None else None
        self.from_user = from_user if from_user is not None else None
        self.caption = caption if caption is not None else None
        self.contact = contact if contact is not None else None
        self.new_chat_members = new_chat_members if new_chat_members is not None else None
        self.bot = bot if bot is not None else None

    @property
    def author(self):
        if self.chat is not None:
            if self.chat.type == Chat.PRIVATE:
                return User(id = self.chat.id, first_name = self.chat.first_name, last_name = self.chat.last_name, username = self.chat.username, bot = self.bot)
            elif self.chat.type == Chat.GROUP: 
                return User(bot = self.bot, id = self.from_user.id, first_name = self.from_user.first_name, last_name = self.from_user.last_name, username = self.from_user.username)
        return None
    
    @classmethod
    def dict(cls, data : dict, bot):
        return cls(bot = bot, message_id = data.get("message_id"), chat = Chat.dict(bot = bot, data = data.get("chat")), date = data.get("date"), text = data.get("text"), from_user = User.dict(bot = bot, data = data.get("from")))
    
    def to_dict(self):
        data = {}
        
        data["message_id"] = self.message_id
        data["date"] = self.date
        data["text"] = self.text
        data["chat"] = self.chat.to_dict()
        data["from"] = self.from_user.to_dict()
        data["caption"] = self.caption
        data["contact"] = self.contact.to_dict()
        
        return data
    
    def delete(self, timeout = (10, 30)):
        message = self.bot.delete_message(chat_id = self.chat.id, message_id = self.message_id)
        return message
    
    def reply(self, text, components = None, reply_to_message_id : bool = True, timeout = (10, 30)):
        json = {}
        json["chat_id"] = f"{self.chat_id}"
        json["text"] = f"{text}"
        if components:
            if type(components) is Components:
                json["reply_markup"] = components.result
            elif type(components) is dict:
                json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = str(self.message_id)
        Message = self.bot.send_message(text = text, components = components, reply_to_message_id = reply_to_message_id if reply_to_message_id else None, timeout = timeout)
        return Message
    
    def reply_invoice(self, title : str, description : str, provider_token : str, prices, photo_url = None, need_name = False, need_phone_number = False, need_email = False, need_shipping_address = False, is_flexible = True, reply_markup = None, reply_to_message_id : bool = True):
        message = self.bot.send_invoice(chat_id = self.chat.id, title = title, description = description, provider_token = provider_token, prices = prices, photo_url = photo_url, need_name = need_name, need_email = need_email, need_phone_number = need_phone_number, need_shipping_address = need_shipping_address, is_flexible = is_flexible ,components = reply_markup, reply_to_message_id = reply_to_message_id if reply_to_message_id else None, timeout = (10, 15))
        return message
    
    def __str__(self):
        return self.message_id
    
    