import requests
from balebot import (Message, Update, User, Components, Price)

class Bot():
    __slots__ = (
        "_bot",
        "token",
        "base_url",
        "base_file_url",
        "_requests"
    )
    def __init__(self, token : str,base_url : str = "https://tapi.bale.ai/", base_file_url : str = "https://tapi.bale.ai/file"):
        self.token = token 
        self.base_url = base_url
        self.base_file_url = base_file_url
        self._bot = None
        self._requests = requests
        if not self.check_token():
            raise f"Bot is not Ready!"
     
    def check_token(self, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        result = self.req("get", "getme", timeout = timeout)
        if result is not None:
            return result.json()["ok"]
        return None


    def get_bot(self, timeout = (5, 10)):
        result = self.req("get", "getme", timeout = timeout)
        if result is not None:
            return User.dict(data = result.json()["result"], bot = self)
        return None
    
    @property
    def bot(self):
        if self._bot is None:
            self._bot = self.get_bot()
        return self._bot
    
    def req(self, mode : str, type : str, data : dict = {}, params : dict = {}, timeout = (5, 10)):
        try:
            if mode == "post":
                return self._requests.post(f"{self.base_url}" + ("" if self.base_url.endswith("/") else "/") + f"bot{self.token}/{type}", json = data, params = params, timeout = timeout)
            elif mode == "get":
                return self._requests.get(f"{self.base_url}" + ("" if self.base_url.endswith("/") else "/" )+ f"bot{self.token}/{type}", params = params, timeout = timeout)
        except:
            pass
        return None
    
    def delete_webhook(self, timeout = (5, 10)):
        if not isinstance(timeout, (tuple, int)):
            return
        result = self.req("get", "deleteWebhook", timeout = timeout)
        if result is not None:
            return result.json()["result"]
        return None

    def send_message(self, chat_id : int, text : str = None,
        sticker = None, files = None, components = None, reply_to_message_id : str = None , timeout = (5, 10)) -> Message:
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        json = {}
        json["chat_id"] = str(chat_id)
        json["text"] = text
        if components:
            if isinstance(components, Components):
                json["reply_markup"] = components.to_dict()
            else:
                json["reply_markup"] = components
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.req("post", "sendMessage", json, timeout = timeout)
        if message is not None:
            json = message.json()
            if json["ok"]: 
                return Message.dict(data = message.json()["result"], bot = self)
        return None

    def send_invoice(self, chat_id : int, title : str, description : str, provider_token : str, prices : Price, reply_to_message_id : str = None,photo_url : str = None, need_name : bool = False, need_phone_number : bool = False, need_email : bool = False, need_shipping_address : bool = False, is_flexible : bool = True, timeout = (5, 10)) -> Message:
        json = {}
        json["chat_id"] = str(chat_id)
        json["title"] = title
        json["description"] = description
        json["provider_token"] = provider_token
        if isinstance(prices, Price):
            json["prices"] = [prices.to_dict()]
        elif isinstance(prices, list):
            key_list = []
            for i in prices:
                if type(i) is Price:
                    key_list.append(i.to_dic())
                else:
                    key_list.append(i)
            json["prices"] = key_list
        if photo_url:
            json["photo_url"] = photo_url
        json["need_name"] = need_name
        json["need_phone_number"] = need_phone_number
        json["need_email"] = need_email
        json["need_shipping_address"] = need_shipping_address
        json["is_flexible"] = is_flexible
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        message = self.req("post", "sendInvoice", data = json, timeout = timeout)
        if message is not None:
            json = message.json()
            if json["ok"]: 
                return Message.dict(data = message.json()["result"], bot = self)
        return None
    
    def delete_message(self, chat_id : str, message_id : str, timeout = (10, 30)):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        Message = self.req(mode = "get", type = "deletemessage", params = {
        "chat_id": str(chat_id),
        "message_id": message_id
        }, timeout = timeout)
        return Message.json()

    def get_updates(self, timeout = (10, 30), offset : int = None, limit : int = None) -> list[Update]:
        result = []
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        
        options = {}
        if offset is not None:
            options["offset"] = offset
        if limit is not None:
            options["limit"] = limit
            
        updates = self.req("post", "getupdates", options, timeout = timeout)
        if updates:
            if not updates.json()["ok"]:
                updates = updates.json()
                raise f"{updates['error_code']} | {updates['description']}"
            for i in updates.json()["result"]:
                if offset is not None and i["update_id"] < offset:
                    continue
                update = Update.dict(data = i, bot = self)
                result.append(update)
            return result
        
        return None