from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bale import Bot
from bale import User

class ContactMessage():
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "id",
        "bot"
    )
    def __init__(self, phone_number : int, id = None, first_name : str = None, last_name : str = None, bot : "Bot" = None):
        """This object shows a Messenge Contact.

        Args:
            phone_number (int)
            id (int): Defaults to None.
            first_name (str): Defaults to None.
            last_name (str): Defaults to None.
            bot (:class:`bale.Bot`): Bot Object. Defaults to None.
        """
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.id = id
        self.bot = bot
            
    @property
    def user(self):    
        if self.id.isdigit():
            return User(bot = self.bot, id = self.id, first_name = self.first_name, last_name = self.last_name)
        return None
            
    @classmethod
    def from_dict(cls, bot, data : dict):
        """
        Args:
            data (dict): Data
            bot (:class:`bale.Bot`): Bot
        """
        return cls(username = data["username"], first_name = data["first_name"], last_name = data["last_name"], id = data["id"], bot = bot)

    def to_dict(self):
        data = {}
        
        data["phone_number"] = self.phone_number
        data["first_name"] = self.first_name
        data["last_name"] = self.last_name
        data["id"] = self.id
        
        return data