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
        Message = post(f"{self.baseclass.base_urll}bot"+ f"{self.baseclass.token}" +"/sendMessage", json = json, timeout = (10, 15)) 
        return Message.json()
    def __str__(self):
        return (str(self.username) + " #" + str(self.id) if self.username else str(self.first_name) + " " + str(self.last_name))
    