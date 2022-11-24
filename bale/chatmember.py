from bale import (Permissions, User)


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
    """This object shows a member in chat

    Attributes
    ----------
        role: :class:`bale.MemberRole`
            User Role
        user: :class:`bale.User`
            User
        permissions: :class:`bale.AdminPermissions`
            User Permissions
    """
    __slots__ = (
        "role", "_user", "permissions"
    )

    def __init__(self, role: "MemberRole" = None, user=None, permissions=None):
        self.role = role
        self._user = user
        self.permissions = permissions

    @property
    def user(self):
        return self._user

    @classmethod
    def from_dict(cls, data: dict):
        return cls(permissions=Permissions.from_dict(data), user=User.from_dict(data.get("user")), role=MemberRole(data.get("status")))

    def __repr__(self):
        return f"<ChatMember role={self.role} user={self._user} permissions={self.permissions}>"
