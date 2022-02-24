from msilib.schema import Class
from requests import post, get
import jdatetime
from jdatetime import timedelta
import datetime
from sqlite3 import connect

class Bot():
    def __init__(self, base_url, token, base_file_url, admin_ids : list, prefix : str):
        self.token = token
        self.base_url = base_url
        self.base_file_url = base_file_url
        self.admin_ids = []
        self.prefix = prefix
        self.commands = {}
        for id in admin_ids:
            if isinstance(id, str):
                if id.isdigit():
                    self.admin_ids.append(int(id)) 
            elif isinstance(id, int):
                self.admin_ids.append(int(id)) 
        
    @classmethod
    def delete_webhook(self, timeout):
        if not isinstance(timeout, (tuple, int)):
            raise "Time out Not true"
        result = get(f"{self.base_url}bot{self.token}/deleteWebhook", timeout=timeout)
        return result.json()["result"]
    
    @classmethod
    def add_handler(self, command_name : str, filter : str):
        if command_name == self.prefix:
            raise "Command Name is not True"
        elif not (filter.lower() == "text" or filter.lower() == "sticker"):
            raise "Filter is not True"
        else:
            if command_name.startswith(self.prefix):
                command_name = command_name.replace(self.prefix, "", 1)
            if not command_name in self.commands:
                self.commands[command_name] = {
                    "filter": f"{filter}"
                }
            else:
                raise "The order already entered"
            
    @classmethod
    def delete_handler(self, command_name : str):
        if command_name == self.prefix:
            raise "Command Name is not True"
        else:
            if command_name.startswith(self.prefix):
                command_name = command_name.replace(self.prefix, "", 1)
            if command_name in self.commands:
                del self.commands[command_name]
            else:
                raise "Command Not Found!"

class Update():
    def __init__(self, update : dict, baseclass):
        self.token = baseclass.token
        self.base_url = baseclass.base_url
        self.base_file_url = baseclass.base_file_url
        self.bot = baseclass.bot
        if update.get("message") is None:
            update = update["callback_query"]   
            self.data =  update["data"]
        self.json = update    
        self.message = Msg(self)
        
    def send_message(self, chat_id, text, reply_markup = None, reply_to_message_id = None, token : str =  None):
        json = {}
        json["chat_id"] = f"{chat_id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        msg = post(f"{self.base_url}bot"+ (f"{token}" if token is not None else f"{self.token}") +"/sendMessage", json = json, timeout = (10, 15)) 
        return msg.json()

class Msg():
    def __init__(self, update):
        self.update = update
        
        if update.json.get("message") is None:
            update = update.json["callback_query"]   
            self.data =  update["callback_query"]["data"]
            self.text = update["callback_query"]["message"].get("text", "")
        else:
            self.text = update.json["message"].get("text", "")
            update = update.json  
        self.message_id = update["message"]["message_id"]
        self.chat_type = update["message"]["chat"]["type"]
        self.chat_id = int(update["message"]["chat"]["id"])
        self.date_code = update["message"]["date"]
        self.date = jdatetime.datetime.fromgregorian(datetime = datetime.datetime.fromtimestamp(update["message"]["date"]))
        self.author = User(self.update)
    
    def delete_message(self):
        msg = get(f"{self.update.base_url}bot{self.update.token}/deletemessage", params = {
        "chat_id": f"{self.chat_id}",
        "message_id": f"{self.message_id}"
        }, timeout = (10, 15))
        return msg.json()
    
    def reply_message(self, text, reply_markup = None, reply_to_message_id : bool = True):
        json = {}
        json["chat_id"] = f"{self.chat_id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = str(self.message_id)
        msg = post(f"{self.update.base_url}bot{self.update.token}/sendMessage", json = json, timeout = (10, 15))
        return msg.json()["result"]
    
    def get_chat_info(self):
        info = get(f"{self.update.base_url}bot{self.update.token}/getChat", params = {
            "chat_id": str(self.chat_id)
        }, timeout = (10, 15))
        return info.json()
    
    def __str__(self):
        return self.message_id
    
class User():
    def __init__(self, update):
        self.update = update
        self.first_name = None
        self.last_name = None
        self.username = None
        self.id = None
        update = update.json
        
        if update.get("message") is None:
            update = update["callback_query"]   
            
        if update["message"]["chat"]["type"] == "private":    
            self.first_name = update["message"]["chat"]["first_name"]
            self.last_name = ''
            self.username = update["message"]["chat"]["username"]
            self.id = int(update['message']['chat']['id'])
            
    def is_bot_admin(self, return_msg_to_user = False):
        db = connect('./data.db')
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM admin WHERE user_id = "{self.update.json["message"]["chat"]["id"]}"')
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result is not None:
            return True 
        if return_msg_to_user:
            self.update.send_message(chat_id = self.update.json["message"]["chat"]["id"], text = '*📛کاربر گرامی شما رئیس بات نیستید!📛*', reply_markup = [[{"text":"سازندگان", "callback_data": "developer"}]])
        return False
    
    def send_message_to_user(self, text, reply_markup = None, reply_to_message_id : int = None):
        json = {}
        json["chat_id"] = f"{self.id}"
        json["text"] = f"{text}"
        if reply_markup:
            json["reply_markup"] = reply_markup
        if reply_to_message_id:
            json["reply_to_message_id"] = reply_to_message_id
        msg = post(f"{self.update.base_urll}bot"+ f"{self.update.token}" +"/sendMessage", json = json, timeout = (10, 15)) 
        return msg.json()
    def __str__(self):
        return str(self.first_name) + str(self.last_name) + f"#{self.id}"