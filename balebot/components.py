from .bot import *

class ReplyMarkup():
    __slots__ = (
        "keyboards", "inlinekeyboards"
    )
    def __init__(self, keyboards = None, inlinekeyboards = None):
        self.keyboards = None
        self.inlinekeyboards = None
        if keyboards is not None:
            self.keyboards = []
            if isinstance(keyboards, list):
                for i in keyboards:
                    if type(i) is dict:
                        key_list = []
                        key_list.append(i)
                        self.keyboards.append(key_list)
                    elif type(i) is list:
                        key_list = []
                        for i in i:
                            if isinstance(i, Keyboard):
                                key_list.append(i.to_dict())
                            else:
                                key_list.append(i)
                        self.keyboards.append(key_list)
            else:
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
                            if isinstance(i, InlineKeyboard):
                                key_list.append(i.to_dict())
                            else:
                                key_list.append(i)
                        self.inlinekeyboards.append(key_list)
            elif type(inlinekeyboards) is dict:
                if "name" in keyboards and "callback_data" in keyboards:
                    self.keyboards.append(keyboards)
        
    @classmethod
    def dict(cls, data : dict, bot):
        return cls(keyboards = data["keyboard"], inlinekeyboards = data["inline_keyboard"], bot = bot)
    
    def to_dict(self):
        data = {}
        
        data["keyboard"] = self.keyboards
        data["inline_keyboard"] = self.inlinekeyboards
        
        return data
        
class InlineKeyboard():
    __slots__ = (
        "text", "callback_data", "bot"
    )
    def __init__(self, text : str, callback_data : str, bot = None):
        self.text = text
        self.callback_data = callback_data
        self.bot = bot
        
    @classmethod
    def dict(cls, data : dict, bot):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text = data["text"], callback_data = data["callback_data"], bot = bot)
    
    def to_dict(self):
        data = {}
        data["text"] = self.text
        data["callback_data"] = self.callback_data
        return data
    
class Keyboard():
    __slots__ = (
        "text", "bot"
    )
    def __init__(self, text: str, bot = None):
        self.text = text
    
    @classmethod
    def dict(cls, data : dict, bot):
        if not data.get("text"):
            return None
        return cls(text = data["text"], bot = bot)
    
    def to_dict(self):
        data = {}
        data["text"] = self.text
        return data