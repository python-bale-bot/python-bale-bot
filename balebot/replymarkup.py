from .bot import *

class ReplyMarkup():
    def __init__(self, keyboards = None, inlinekeyboards = None):
        self.keyboards = None
        self.inlinekeyboards = None
        if keyboards is not None:
            self.keyboards = []
            if type(keyboards) is list:
                for i in keyboards:
                    if type(i) is dict:
                        key_list = []
                        key_list.append(i)
                        self.keyboards.append(key_list)
                    elif type(i) is list:
                        key_list = []
                        for i in i:
                            key_list.append({"text": i.text})
                        self.keyboards.append(key_list)
            elif type(keyboards) is dict:
                if "name" in keyboards:
                    self.keyboards.append(keyboards)
        if inlinekeyboards is not None:
            self.inlinekeyboards = []
            if type(inlinekeyboards) is list:
                for i in inlinekeyboards:
                    if type(i) is dict:
                        key_list = []
                        key_list.append(i)
                        self.inlinekeyboards.append(key_list)
                    elif type(i) is list:
                        key_list = []
                        for i in i:
                            key_list.append({"text": i.text, "callback_data": i.callback_data})
                        self.inlinekeyboards.append(key_list)
            elif type(inlinekeyboards) is dict:
                if "name" in keyboards and "callback_data" in keyboards:
                    self.keyboards.append(keyboards)
        self.result =  {}
        if self.keyboards:
            self.result["keyboard"] = self.keyboards
        if self.inlinekeyboards:
            self.result["inline_keyboard"] = self.inlinekeyboards
        
    
        
class InlineKeyboard():
    def __init__(self, text : str, callback_data : str):
        self.text = text
        self.callback_data = callback_data
    @classmethod
    def dict(cls, data : dict):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text = data["text"], callback_data = data["callback_data"])
    
    def to_dict(self):
        data = {}
        data["text"] = self.text
        data["callback_data"] = self.callback_data
        return data
    
class Keyboard():
    def __init__(self, text: str):
        self.text = text
    
    @classmethod
    def dict(cls, data : dict):
        if not data.get("text"):
            return None
        return cls(text = data["text"])
    
    def to_dict(self):
        data = {}
        data["text"] = self.text
        return data