from bale import (AdminPermissions, User)


class MemberRole:
    """Member Role"""
    OWNER = "creator"
    ADMIN = "administrator"
    __slots__ = ("_role",)

    def __init__(self, _role: str):
        self._role = _role

    def is_owner(self):
        """Member have owner role?"""
        return self._role == self.OWNER

    def is_admin(self):
        """Member have admin role?"""
        return self._role == self.ADMIN


class ChatMember:
    """This object shows a user in chat

        Args:
            role (MemberRole): User Role. Defaults to None.
            user (:class:`bale.User`): User. Defaults to None.
            permissions (:class:`bale.AdminPermissions`): User Permissions. Defaults to None.
    """
    __slots__ = (
        "role", "_user", "permissions"
    )

    def __init__(self, role: "MemberRole" = None, user=None, permissions=None):
        self.role = role
        self._user = user
        self.permissions = permissions

    @classmethod
    def from_dict(cls, data: dict):
        """
        Args:
            data (dict): Data
        """
        return cls(permissions=AdminPermissions.from_dict(data), user=User.from_dict(data.get("user")), role=MemberRole(data.get("status")))
