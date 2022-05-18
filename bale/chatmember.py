from bale import (AdminPermissions, User)

class Role:
    OWNER = "creator"
    ADMIN = "administrator" 
    
class ChatMember:
    __slots__ = (
        "role", "user", "permissions"
    )
    
    def __init__(self, role : str = None, user = None, permissions = None):
        self.role = role
        self.user = user
        self.permissions = permissions
    
    @property
    def is_admin(self):
        return True if self.role == Role.ADMIN or self.role == Role.OWNER else False
    
    @property
    def is_owner(self):
        return True if self.role == Role.OWNER else False
    
    @classmethod
    def from_dict(cls, data : dict):
        
        permissions = AdminPermissions.PERMISSIONS_LIST
        for i in AdminPermissions.PERMISSIONS_LIST:
            permissions[i] = data.get(i, False)
        
        return cls(permissions = permissions, user = User.from_dict(data.get["user"]), role = data.get("status"))
    