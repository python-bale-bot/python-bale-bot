


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
        Message = get(f"{self.baseclass.base_url}bot{self.baseclass.token}/deletemessage", params = {
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
        Message = post(f"{self.baseclass.base_url}bot{self.baseclass.token}/sendMessage", json = json, timeout = (10, 15))
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
        Message = post(f"{self.baseclass.base_url}bot{self.baseclass.token}/sendMessage", json = json, timeout = (10, 15))
        return Message.json()["result"]
    
    def get_chat_info(self, timeout):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        info = get(f"{self.baseclass.base_url}bot{self.baseclass.token}/getChat", params = {
            "chat_id": str(self.chat_id)
        }, timeout = timeout)
        return info.json()
    
    def __str__(self):
        return self.message_id