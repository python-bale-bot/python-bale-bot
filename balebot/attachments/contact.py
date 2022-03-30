from ..user import User

class ContactMessage():
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "id",
        "bot"
    )
    def __init__(self, phone_number : int, id = None,first_name : str = None, last_name : str = None, bot = None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.id = id
            
    @property
    def user(self):    
        if self.id.isdigit():
            return User(bot = self, id = self.id, first_name = self.first_name, last_name = self.last_name)
        return None
            
    @classmethod
    def dict(cls, bot, data : dict):
        return cls(username = data["username"], first_name = data["first_name"], last_name = data["last_name"], id = data["id"], bot = bot)

    def to_dict(self):
        data = {}
        
        data["phone_number"] = self.phone_number
        data["first_name"] = self.first_name
        data["last_name"] = self.last_name
        data["id"] = self.id
        
        return data