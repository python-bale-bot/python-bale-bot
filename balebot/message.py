import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balebot import Bot, User, Chat
    
from balebot import Components, Audio, ContactMessage, Location

class Message():
    __slots__ = (
        "text", "caption", "forward_from", "author","contact", "chat","message_id", "date_code", "date", "author", "edit_date", "audio", "document", "photo", "voice", "location", "invoice"
    )
    def __init__(self, message_id : str, date : datetime.datetime, text = None, caption : str = None, forward_from : "User" = None, contact : ContactMessage = None, chat : Chat = None, document = None, photo = None, voice : Audio = None, location : Location = None, invoice = None, bot : 'Bot' = None):
        self.message_id = message_id if message_id is not None else None
        self.date = date if date is not None else None
        
        self.text = text if text is not None else None
        self.chat = chat if chat is not None else None
        self.forward_from = forward_from if forward_from is not None else None
        self.caption = caption if caption is not None else None
        self.contact = contact if contact is not None else None
        self.bot = bot if bot is not None else None

    @property
    def author(self):
        if self.chat is not None:
            if self.chat.type == Chat.PRIVATE:
                self.author = User(id = self.chat.id, first_name = self.chat.first_name, last_name = self.chat.last_name, username = self.chat.username, bot = self.bot)
            elif self.chat.type == Chat.GROUP: 
                self.author = User(bot = self.bot, id = self.forward_from.id, first_name = self.forward_from.first_name, last_name = self.forward_from.last_name, username = self.forward_from.username)
        return None
    
    @classmethod
    def dict(cls, data : dict, bot):
        return cls(bot = bot)
    
    def to_dict(self):
        data = {}
        
        data["message_id"] = self.message_id
        data["date"] = self.date
        data["text"] = self.text
        data["chat"] = self.chat.to_dict()
        data["forward_from"] = self.forward_from.to_dict()
        data["caption"] = self.caption
        data["contact"] = self.contact.to_dict()
        
        return data
    
    def delete(self, timeout):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        Message = self.bot.req(mode = "get", type = "deletemessage", params = {
        "chat_id": str(self.chat.id),
        "message_id": self.message_id
        }, timeout = timeout)
        return Message.json()
    
    def reply(self, text, components = None, reply_to_message_id : bool = True):
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
        Message = self.bot.send_message(text = text, components = components, reply_to_message_id = reply_to_message_id if reply_to_message_id else None, timeout = (10, 15))
        return Message
    
    def reply_invoice(self, title : str, description : str, provider_token : str, prices, photo_url = None, need_name = False, need_phone_number = False, need_email = False, need_shipping_address = False, is_flexible = True, reply_markup = None, reply_to_message_id : bool = True):
        message = self.bot.send_invoice(chat_id = self.chat.id, title = title, description = description, provider_token = provider_token, prices = prices, photo_url = photo_url, need_name = need_name, need_email = need_email, need_phone_number = need_phone_number, need_shipping_address = need_shipping_address, is_flexible = is_flexible ,components = reply_markup, reply_to_message_id = reply_to_message_id if reply_to_message_id else None, timeout = (10, 15))
        return message
    
    def __str__(self):
        return self.message_id
    
    