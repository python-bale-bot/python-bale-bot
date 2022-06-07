"""Import `bale.Permissions` and `bale.User`"""
from bale import (AdminPermissions, User)


class Role:
    """Member Role"""
    __slots__ = ()
    OWNER = "creator"
    ADMIN = "administrator"

    def __init__(self):
        pass


class ChatMember:
    """This object shows a user in chat

        Args:
            role (str): User Role. Defaults to None.
            user (:class:`bale.user`): User. Defaults to None.
            permissions (:class:`bale.AdminPermissions`): User Permissions. Defaults to None.
    """
    __slots__ = (
        "role", "user", "permissions"
    )

    def __init__(self, role: str = None, user=None, permissions=None):
        self.role = role
        self.user = user
        self.permissions = permissions

    @property
    def is_admin(self):
        """if the member was the admin, it will be returned "True" and otherwise "False".

        Returns:
            bool: if the member was the admin, it will be returned "True" and otherwise "False".
        """
        return True if self.role == Role.ADMIN or self.role == Role.OWNER else False

    @property
    def is_owner(self):
        """if the member was the owner, it will be returned "True" and otherwise "False".

        Returns:
            bool: if the member was the owner, it will be returned "True" and otherwise "False".
        """
        return True if self.role == Role.OWNER else False

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        permissions = {}
        for i in AdminPermissions.PERMISSIONS_LIST:
            permissions[i] = data.get(i, False)

        return cls(permissions=permissions, user=User.from_dict(data.get("user")), role=data.get("status"))
