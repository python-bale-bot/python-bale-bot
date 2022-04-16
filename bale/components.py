class Components():
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
                    elif type(i) is Keyboard:
                        self.keyboards.append([i.to_dict()])
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
                    elif type(i) is InlineKeyboard:
                        self.inlinekeyboards.append([i.to_dict()])
            elif type(inlinekeyboards) is dict:
                if "name" in inlinekeyboards and "callback_data" in inlinekeyboards:
                    self.inlinekeyboards.append(inlinekeyboards)
        
    @classmethod
    def dict(cls, data : dict):
        return cls(keyboards = data["keyboard"], inlinekeyboards = data["inline_keyboard"])
    
    def to_dict(self):
        data = {}
        
        data["keyboard"] = self.keyboards
        data["inline_keyboard"] = self.inlinekeyboards
        
        return data
        
class InlineKeyboard():
    __slots__ = (
        "text", "callback_data", "url", "switch_inline_query", "switch_inline_query_current_chat", "pay"
    )
    def __init__(self, text : str, callback_data : str = None, url : str = None, switch_inline_query : str = None, switch_inline_query_current_chat : str = None, pay : bool = False):
        self.text = text
        self.callback_data = callback_data if callback_data is not None else None
        self.url = url if url is not None else None
        self.switch_inline_query = switch_inline_query if switch_inline_query is not None else switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat if switch_inline_query_current_chat is not None else None
        self.pay = pay if pay else False
        
    @classmethod
    def dict(cls, data : dict):
        if not data.get("text") or not data.get("callback_data"):
            return None
        return cls(text = data["text"], callback_data = data.get("callback_data"), url = data.get("url"), switch_inline_query = data.get("switch_inline_query"), switch_inline_query_current_chat = data.get("switch_inline_query_current_chat"), pay = data.get("pay", False))
    
    def to_dict(self):
        data = {}
        data["text"] = self.text
        
        if self.callback_data:
            data["callback_data"] = self.callback_data
        
        if self.url:
            data["url"] = self.url
        
        if self.switch_inline_query:
            data["switch_inline_query"] = self.switch_inline_query
            
        if self.switch_inline_query_current_chat:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
            
        if self.pay:
            data["pay"] = self.pay
        
        return data
    
class Keyboard():
    __slots__ = (
        "text"
    )
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