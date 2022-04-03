import requests
from balebot import (Message, Update, User, Components, Price)

class Bot():
    __slots__ = (
        "_bot",
        "token",
        "base_url",
        "base_file_url",
        "offset",
        "_requests"
    )
    def __init__(self, token : str,base_url : str = "https://tapi.bale.ai/", base_file_url : str = "https://tapi.bale.ai/file"):
        self.token = token 
        self.base_url = base_url
        self.base_file_url = base_file_url
        self._bot = None
        self._requests = requests
        self.offset = None   
        if not self.check_token(self.token):
            raise f"Bot is not Ready!"
     
    def check_token(self, token, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        try:
            result = self._requests.get(self.base_url + "bot" + token + "/getme", timeout = timeout)
        except Exception as error:
            return None
        return result.json()["ok"]

    def get_bot(self, timeout = (5, 10)):
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
    
    def req(self, mode : str, type : str,data : dict = None, params : dict = None,timeout = (5, 10)):
        try:
            if mode == "post":
                return self._requests.post(f"{self.base_url}" + "" if self.base_url.endswith("/") else "/"+ f"bot{self.token}/{type}", json = data, params = params, timeout = timeout)
            elif mode == "get":
                return self._requests.get(f"{self.base_url}" + "" if self.base_url.endswith("/") else "/"+ f"bot{self.token}/{type}", json = data, params = params, timeout = timeout)
        except:
            return None
    
    def delete_webhook(self, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        result = self.req("get", "deleteWebhook")
        return result.json()["result"]

    def send_message(self, chat_id : int, text : str = None,
        sticker = None, files = None, components = None, reply_to_message_id : str = None , timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
                raise "Time out Not true"
        json = {}
        json["chat_id"] = str(chat_id)
        json["text"] = text
        if components:
            if isinstance(components, Components):
                json["reply_markup"] = components
            else:
                json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.req("post", "sendMessage", json)
        json = message.json()
        if json["ok"]: 
            return Message.dict(data = message.json()["result"], bot = self)
        else:
            return None

    def send_invoice(self, chat_id : int, title : str, description : str, provider_token : str, prices : Price, reply_to_message_id : str = None,photo_url : str = None, need_name : bool = False, need_phone_number : bool = False, need_email : bool = False, need_shipping_address : bool = False, is_flexible : bool = True, components : Components = None, timeout = (5, 10)):
        json = {}
        json["chat_id"] = str(chat_id)
        json["title"] = title
        json["description"] = description
        json["provider_token"] = provider_token
        if isinstance(prices, Price):
            json["prices"] = prices.to_dict()
        else:
            json["prices"] = prices
        if photo_url:
            json["photo_url"] = photo_url
        json["need_name"] = need_name
        json["need_phone_number"] = need_phone_number
        json["need_email"] = need_email
        json["need_shipping_address"] = need_shipping_address
        json["is_flexible"] = is_flexible
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        if components:
            if isinstance(components, Components):
                json["reply_markup"] = components.to_dict()
            else:
                json["reply_markup"] = components
        message = self.req("post", "sendInvoice", data = json, timeout = timeout)
        json = message.json()
        if json["ok"]: 
            return Message.dict(data = message.json()["result"], bot = self)
        else:
            return None

    def get_updates(self, timeout = (10, 30), offset : int = None, limit : int = None):
        result = []
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        
        if offset is None:
            offset = self.offset
            
        options = {}
        if offset is not None:
            options["offset"] = offset
        if limit is not None:
            options["limit"] = limit
            
        updates = self.req("post", "getupdates", options)
        if updates:
            if not updates.json()["ok"]:
                updates = updates.json()
                raise f"{updates['error_code']} | {updates['description']}"
            if len(updates.json()["result"]) != 0:
                self.offset = int(updates.json()["result"][-1]["update_id"]) 
        else:
            return None
        for i in updates.json()["result"]:
            update = Update.dict(data = i, bot = self)
            result.append(update)
        return result