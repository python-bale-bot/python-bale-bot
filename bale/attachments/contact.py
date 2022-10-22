from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bale import Bot, User


class ContactMessage:
    """This object shows a Message Contact.

    Attributes
    ----------
        phone_number: int
        first_name: Optional[:class:`str`]
        last_name: Optional[:class:`str`]
        user: Optional[:class:`bale.User`]
    """
    __slots__ = (
        "phone_number",
        "first_name",
        "last_name",
        "id",
        "bot"
    )

    def __init__(self, phone_number: int, first_name: str = None, last_name: str = None, bot: "Bot" = None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.bot = bot

    @property
    def user(self):
        if self.id:
            return User(bot=self.bot, user_id=self.id, first_name=self.first_name, last_name=self.last_name)
        return None

    @classmethod
    def from_dict(cls, data: dict, bot: "Bot" = None):
        return cls(first_name=data["first_name"], last_name=data["last_name"],
                   bot=bot, phone_number=data["phone_number"])

    def to_dict(self):
        data = {"phone_number": self.phone_number, "first_name": self.first_name, "last_name": self.last_name}

        return data
