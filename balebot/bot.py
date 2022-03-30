import requests
import jdatetime
from jdatetime import timedelta
import datetime
from .replymarkup import ReplyMarkup, InlineKeyboard, Keyboard

class Bot():
    __slots__ = (
        "_bot",
        "token",
        "base_url",
        "base_file_url"
    )
    def __init__(self, token : str,base_url : str = "", base_file_url : str = ""):
        self.token = token 
        self.base_url = base_url
        self.base_file_url = base_file_url
        self.bot = {}
        self._requests = requests
        self.offset = None   
        if not self.check_token():
            raise f"Bot is not Ready!"
     
    def check_token(self, token, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        try:
            result = self._requests.get(self.base_url + "bot" + self.token + "/getme", timeout = timeout)
        except Exception as error:
            return error
        self.bot = User(result.json()["result"], self)
        return result.json()["ok"]
    
    def delete_webhook(self, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        result = self._requests.get(f"{self.base_url}bot{self.token}/deleteWebhook", timeout=timeout)
        return result.json()["result"]

    def send_message(self, chat_id : int, text : str = None,
        sticker = None, files = None, reply_markup = None, reply_to_message_id : str = None, token : str =  None , timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
                raise "Time out Not true"
        json = {}
        json["chat_id"] = f"{chat_id}"
        json["text"] = f"{text}"
        if reply_markup:
            if isinstance(reply_markup, ReplyMarkup):
                json["reply_markup"] = reply_markup
            else:
                json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        Message = self._requests.post(f"{self.base_url}bot"+ (f"{token}" if token is not None else f"{self.token}") +"/sendMessage", json = json, timeout = timeout) 
        return Message.json()

    def get_updates(self, timeout, offset : int = None, limit : int = None):
        if offset is None:
            offset = self.offset
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        options = {}
        if offset is not None:
            options["offset"] = offset
        if limit is not None:
            options["limit"] = limit
        while True:
            try:
                updates = self._requests.post(self.base_url + "bot" + self.token + "/getupdates", json = options, timeout = timeout)
                print(updates.json())
                if not updates.json()["ok"]:
                    updates = updates.json()
                    raise f"{updates['error_code']} | {updates['description']}"
                if len(updates.json()["result"]) != 0:
                    self.offset = int(updates.json()["result"][-1]["update_id"]) 
                break   
            except:
                pass
        result = []
        for i in updates.json()["result"]:
            update = Update(i, self)
            result.append(update)
        return result

class Update():
    def __init__(self, update : dict, base_class):
        self.__dict__ = {
            "id": None, "token": None, "base_url" : None, "base_file_url": None, "bot": None, "base_class": None, "json": None, "type": None, "message": None, "successful_payment": None, "callback_query": None
        }
        self.id = int(update.get("update_id"))
        self.token = base_class.token
        self.base_url = base_class.base_url
        self.base_file_url = base_class.base_file_url
        self.bot = base_class.bot
        self.base_class = base_class
        self.json = update    
        self.type = "unknown"
        if update.get("callback_query"):
            self.type = "callback_query"
            self.callback_query = CallbackQuery(update.get("callback_query"), self)
            self.message : Message = self.callback_query.message
        elif update.get("message"):
            self.type = "message"
            self.message : Message = Message(update["message"], self)
        elif update.get("edited_message"):
            self.type = "edited_message"
            self.message : Message = Message(update.get("edited_message"), self)
            
        
        
    def send_message(self, chat_id, timeout, text = None,
        sticker = None, files = None, reply_markup = None, reply_to_message_id = None, token : str =  None ):
        if not isinstance(timeout, (tuple, int)):
                raise "Time out Not true"
        json = {}
        json["chat_id"] = f"{chat_id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        Message = self._requests.post(f"{self.base_url}bot"+ (f"{token}" if token is not None else f"{self.token}") +"/sendMessage", json = json, timeout = timeout) 
        return Message.json()

class Message():
    def __init__(self, update : dict, baseclass):
        self.__dict__ = {
            "update": None, "baseclass": None, "text": None,"caption": None, "forward_from": None, "contact": None, "message_id": None, "chat_type": None, "chat_id": None, "chat_id": None, "date_code": None, "date": None, "author": None, "edit_date": None, "audio": None, "document": None, "photo": None, "voice": None, "location": None, "invoice": None
        }
        self.update = update
        self.baseclass = baseclass
        if update.get("text"):
            self.text = str(update["text"])
        if update.get("caption"):
            self.caption = str(update["caption"])
        if update.get("forward_from"):
            self.forward_from = User(update["forward_from"], self.baseclass)
        if update.get("contact"):
            self.contact = ContactMessage(update["contact"], self.baseclass)
        self.message_id = update["message_id"]
        self.chat_type = update["chat"]["type"]
        self.chat_id = int(update["chat"]["id"])
        self.date_code = update["date"]
        self.date = jdatetime.datetime.fromgregorian(datetime = datetime.datetime.fromtimestamp(update["date"]))
        self.author = User(self.update["chat"] if self.chat_type == "private" else self.update["from"], self.baseclass)
    
    def delete(self, timeout):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        Message = self._requests.get(f"{self.baseclass.base_url}bot{self.baseclass.token}/deletemessage", params = {
        "chat_id": f"{self.chat_id}",
        "message_id": f"{self.message_id}"
        }, timeout = timeout)
        return Message.json()
    
    def reply(self, text, components = None, reply_to_message_id : bool = True):
        json = {}
        json["chat_id"] = f"{self.chat_id}"
        json["text"] = f"{text}"
        if components:
            if type(components) is ReplyMarkup:
                json["reply_markup"] = components.result
            elif type(components) is dict:
                json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = str(self.message_id)
        Message = self._requests.post(f"{self.baseclass.base_url}bot{self.baseclass.token}/sendMessage", json = json, timeout = (10, 15))
        return Message.json()["result"]
    
    def reply_message_invoice(self, title, description, provider_token, prices, photo_url = False, need_name = False, need_phone_number = False, need_email = False, need_shipping_address = False, is_flexible = True, reply_markup = None):
        json = {}
        json["chat_id"] = f"{self.chat_id}"
        json["title"] = f"{title}"
        json["description"] = f"{description}"
        json["provider_token"] = f"{provider_token}"
        json["prices"] = prices
        if photo_url:
            json["photo_url"] = photo_url
        if need_name:
            json["need_name"] = need_name
        if need_phone_number:
            json["need_phone_number"] = need_phone_number
        if need_email:
            json["need_email"] = need_email
        if need_shipping_address:
            json["need_shipping_address"] = need_shipping_address
        if is_flexible:
            json["is_flexible"] = is_flexible
        if reply_markup:
            json["reply_markup"] = reply_markup
        Message = self._requests.post(f"{self.baseclass.base_url}bot{self.baseclass.token}/sendMessage", json = json, timeout = (10, 15))
        return Message.json()["result"]
    
    def get_chat_info(self, timeout):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        info = self._requests.get(f"{self.baseclass.base_url}bot{self.baseclass.token}/getChat", params = {
            "chat_id": str(self.chat_id)
        }, timeout = timeout)
        return info.json()
    
    def __str__(self):
        return self.message_id

class CallbackQuery():
    def __init__(self, update, baseclass):
        self.baseclass = baseclass
        self.data = update["data"]
        self.message = Message(update["message"], self.baseclass)
        self.id = int(update["id"])
        self.inline_message_id = str(update["inline_message_id"])
        self.from_user = User(update["from"], self.baseclass) 
 
class User():
    def __init__(self, update : dict, baseclass):
        self.baseclass = baseclass
        self.update = update
        self.first_name = None
        self.last_name = None
        self.username = None
        self.id = None  
        self.mention = None
        if update.get("first_name"):
            self.first_name = update["first_name"]
        if update.get("last_name"):
            self.last_name = update["last_name"]
        if update.get("username"):
            self.username = update["username"]
            self.mention = "[{username}](https://ble.ir/@{username})".format(username = self.username)
        if update.get("id"):
            self.id = int(update['id'])
        
    
    def send_message_to_user(self, text, reply_markup = None, reply_to_message_id : int = None):
        json = {}
        json["chat_id"] = f"{self.id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        Message = self._requests.post(f"{self.baseclass.base_urll}bot"+ f"{self.baseclass.token}" +"/sendMessage", json = json, timeout = (10, 15)) 
        return Message.json()
    def __str__(self):
        return (str(self.username) + " #" + str(self.id) if self.username else str(self.first_name) + " " + str(self.last_name))
    
class ContactMessage():
    def __init__(self, update : dict, baseclass):
        self.update = update
        self.baseclass = baseclass
        self.user = None
        if update.get("phone_number"):
            self.phone_number = str(update["phone_number"])
        if update.get("first_name"):
            self.first_name = str(update["first_name"])
        if update.get("last_name"):
            self.last_name = str(update["last_name"])
        if update.get("user_id"):
            self.user_id = str(update["user_id"])
            
        if self.user_id.isdigit():
            self.user = User(update, self.baseclass)

class Audio():
    def __init__(self, update : dict):
        self.update = update
        self.file_id = update["file_id"]
        self.title = update["title"]
        self.file_size = update["file_size"]
        self.mime_type = update["mime_type"]

class Location():
    def __init__(self, update : dict, longitude : int, latitude : int):
        self.update = update
        self.longitude = longitude
        self.latitude = latitude
        self.link = f"https://maps.google.com/maps?q=loc:{self.longitude},{self.latitude}"
    

        
                
    