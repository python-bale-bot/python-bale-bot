import requests
import jdatetime
from jdatetime import timedelta
import datetime
from .user import User
from .components import ReplyMarkup, InlineKeyboard, Keyboard


class Bot():
    __slots__ = (
        "_bot",
        "token",
        "base_url",
        "base_file_url"
    )
    def __init__(self, token : str,base_url : str = "", base_file_url : str = "", bot = None):
        self.token = token 
        self.base_url = base_url
        self.base_file_url = base_file_url
        self._bot = bot
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
        return result.json()["ok"]

    def get_bot(self):
        try:
            result = self._requests.get(self.base_url + "bot" + self.token + "/getme", timeout = timeout)
        except Exception as error:
            return None
        return User.dict(data = result.json()["result"], bot = self)
    
    @property
    def bot(self):
        if self._bot is None:
            self._bot = self.get_bot()
        return self._bot
    
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

class CallbackQuery():
    def __init__(self, update, baseclass):
        self.baseclass = baseclass
        self.data = update["data"]
        self.message = Message(update["message"], self.baseclass)
        self.id = int(update["id"])
        self.inline_message_id = str(update["inline_message_id"])
        self.from_user = User(update["from"], self.baseclass) 
    
    

        
                
    