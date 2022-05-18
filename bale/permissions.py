class AdminPermissions:
    __slots__ = (
    "can_be_edited",
    "can_change_info",
    "can_post_messages",
    "can_edit_messages",
    "can_delete_messages",
    "can_invite_users",
    "can_restrict_members",
    "can_pin_messages",
    "can_promote_members",
    "can_send_messages",
    "can_send_media_messages"
    )
    def __init__(self, can_be_edited : bool = False, can_change_info : bool = False, can_post_messages : bool = False, can_edit_messages : bool = False, can_delete_messages : bool = False, can_invite_users : bool = False, can_restrict_members : bool = False, can_pin_messages : bool = False, can_promote_members : bool = False, can_send_messages : bool = False, can_send_media_messages : bool = False):
        self.can_be_edited = can_be_edited
        self.can_change_info = can_change_info
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_delete_messages = can_delete_messages
        self.can_invite_users = can_invite_users
        self.can_restrict_members = can_restrict_members
        self.can_pin_messages = can_pin_messages
        self.can_promote_members = can_promote_members
        self.can_send_messages = can_send_messages
        self.can_send_media_messages = can_send_media_messages
        
    @staticmethod
    def from_dict(cls, data : dict):
        return cls(can_be_edited = data.get("can_be_edited"), can_change_info = data.get("can_change_info"), can_post_messages = data.get("can_post_messages"), can_edit_messages = data.get("can_edit_messages"), can_delete_messages = data.get("can_delete_messages"), can_invite_users = data.get("can_invite_users"), can_restrict_members = data.get("can_restrict_members"), can_pin_messages = data.get("can_pin_messages"), can_promote_members = data.get("can_promote_members"), can_send_messages = data.get("can_send_messages"), can_send_media_messages = data.get("can_send_media_messages"))
    
