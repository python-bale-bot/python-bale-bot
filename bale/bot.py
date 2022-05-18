import requests
from bale import (Message, Update, User, Components, Chat, Price)

class Bot():
    __slots__ = (
        "_user",
        "token",
        "base_url",
        "base_file_url",
        "_requests"
    )
    def __init__(self, token : str,base_url : str = "https://tapi.bale.ai/", base_file_url : str = "https://tapi.bale.ai/file"):
        self.token = token 
        self.base_url = base_url
        self.base_file_url = base_file_url
        self._requests = requests
        self._user = self.check_token()
        if not self._user:
            raise f"Bot is not Ready!"
     
    def check_token(self, timeout = (30, 10)) -> bool:
        if not isinstance(timeout, (tuple, int)):
            return
        result = self.req("get", "getme", timeout = timeout)
        if result is not None:
            return result.json()["ok"]
        return None


    def get_bot(self, timeout = (30, 10)) -> User:
        result = self.req("get", "getme", timeout = timeout)
        if result is not None:
            return User.from_dict(data = result.json()["result"], bot = self)
        return None
    
    @property
    def bot(self) -> User:
        """Get Bot User

        Returns:
            :class:`bale.User` or None
        """
        if self._user is None:
            self._user = self.get_bot()
        return self._user
    
    def req(self, mode : str, type : str, data : dict = {}, params : dict = {}, timeout = (5, 10)) -> requests.Response:
        try:
            if mode == "post":
                return self._requests.post(f"{self.base_url}" + ("" if self.base_url.endswith("/") else "/") + f"bot{self.token}/{type}", json = data, params = params, timeout = timeout)
            elif mode == "get":
                return self._requests.get(f"{self.base_url}" + ("" if self.base_url.endswith("/") else "/" )+ f"bot{self.token}/{type}", params = params, timeout = timeout)
        except:
            pass
        return None
    
    def delete_webhook(self, timeout = (5, 10)) -> bool:
        """Delete Webhook

        Args:
            timeout (tuple, optional): Defaults to (5, 10).

        Returns:
            bool: If done "True" If not "False"
        """
        if not isinstance(timeout, (tuple, int)):
            return
        result = self.req("get", "deleteWebhook", timeout = timeout)
        if result is not None:
            return result.json()["result"]
        return False

    def send_message(self, chat_id : str, text : str = None, components = None, reply_to_message_id : str = None , timeout = (5, 10)) -> Message:
        """Delete Webhook
        
        Args:
            chat_id (int): Chat ID.
            text (str): Message Text. 
            components (bot.Components, dict): Message Components. 
            reply_to_message_id (str): Reply Message ID. 
            timeout (tuple, int): _description_. Defaults to (5, 10).
        Raises:
            :class:`bale.Error`
        Returns:
            :class:`bale.Message`: On success, the sent Message is returned.
        """
        
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
                return Message.from_dict(data = message.json()["result"], bot = self)
        return None

    # def send_photo(self, chat_id : str, photo, caption : str = None, reply_to_message_id : str = None, timeout = (5, 10)):
    #     if not isinstance(timeout, (tuple, int)):
    #         raise "Time out Not true"
    #     json = {}
    #     json["chat_id"] = chat_id
    #     json["photo"] = photo
    #     json["caption"] = caption
    #     json["reply_to_message_id"] = reply_to_message_id
        
    #     message = self.req("post", "SendPhoto", data = json, timeout = timeout)
    #     if message is not None:
    #         json = message.json()
    #         if json["ok"]: 
    #             return Message.from_dict(data = message.json()["result"], bot = self)
    #     return None

    def send_invoice(self, chat_id : str, title : str, description : str, provider_token : str, prices : Price, reply_to_message_id : str = None, photo_url : str = None, need_name : bool = False, need_phone_number : bool = False, need_email : bool = False, need_shipping_address : bool = False, is_flexible : bool = True, timeout = (5, 10)) -> Message:
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
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
                return Message.from_dict(data = message.json()["result"], bot = self)
        return None
    
    def edit_message(self, chat_id : str, message_id : str, newtext : str, components = None, timeout = (10, 30)):
        """
        Args:
            chat_id (str): Chat Id.
            message_id (str): Message Id.
            newtext (str): New Content For Message.
            components (:class:`bale.Components`, optional): Components. Defaults to None.
            timeout (tuple, optional): _description_. Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Return:
            None
        """
        data = {}
        data["chat_id"] = chat_id
        data["message_id"] = message_id
        data["text"] = newtext
        if components:
            if isinstance(components, Components):
                data["reply_markup"] = components.to_dict()
            else:
                data["reply_markup"] = components
        
        Response = self.req("post", "editMessageText", data = data, timeout = timeout)
        return Response
        
    
    def delete_message(self, chat_id : str, message_id : str, timeout = (10, 30)):
        """Delete Message 
        
        In Channel or Group:
            If it is a group or channel Manager, it can delete a message from (group or channel).

        In private message (PV):
            If the message was sent by a bot, it can be deleted with this method

        Args:
            chat_id (str): _description_
            message_id (str): _description_
            timeout (tuple, optional): _description_. Defaults to (10, 30).

        Return:
            bool: If done "True" If not "False"
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        Message = self.req(mode = "get", type = "deletemessage", params = {
        "chat_id": str(chat_id),
        "message_id": message_id
        }, timeout = timeout)
        return Message.json()

    def get_chat(self, chat_id : str, timeout = (10, 30)):
        """Get Chat Object.

        Args:
            chat_id (str): Chat Id.
            timeout (tuple, optional): TimeOut. Defaults to (10, 30).
        Raises:
            None
            # :class:`bale.Error`
        Return:
            :class:`bale.Chat`: On success, the sent Message is returned.
        """
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        
        chat = self.req("get", "getchat", params = {
            "chat_id": chat_id
        })
        if chat is not None:
            json = chat.json()
            if json["ok"]: 
                return Chat.from_dict(json["result"], bot = self) if chat is not None else None
        return None

    def get_chat_administrators(self, chat_id : str, timeout = (10, 30)):
        """This service can be used to display admins of a group or channel.

        Args:
            chat_id (str): Group ID
            timeout (tuple, int): Defaults to (10, 30).
        Raises:
            :class:`bale.Error`
        Returns:
            List[:class:`bale.ChatMember`]
        """
        pass

    def get_updates(self, timeout = (10, 30), offset : int = None, limit : int = None):
        """Use this method to receive incoming updates using long polling. 

        Args:
            timeout (tuple, int, optional): Defaults to (10, 30).
            offset (int, optional): Defaults to None.
            limit (int, optional): Defaults to None.

        Raises:
            :class:`bale.Error`

        Returns:
            List[:class:`bale.Update`]
        """
        
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
                update = Update.from_dict(data = i, bot = self)
                result.append(update)
            return result if result != [] else None
        
        return None