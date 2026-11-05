#  An API wrapper for Bale written in Python
#  Copyright (c) 2022-2026
#  Kian Ahmadian <devs@python-bale-bot.ir>
#  All rights reserved.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
#  This software is licensed under the GNU General Public License v2.0.
#  See the accompanying LICENSE file for details.
#
#  You should have received a copy of the GNU General Public License v2.0
#  along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# This software is licensed under the GNU General Public License v2.0.
# See the accompanying LICENSE file for details.
#
# You should have received a copy of the GNU General Public License v2.0
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
from collections.abc import Hashable, Iterator
from enum import Enum as _Enum
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from .context import Context


__all__ = (
    "BALE_BASE_URL",
    "BALE_API_BASE_URL",
    "BALE_API_BUSINESS_URL",
    "BALE_API_FILE_URL",
    "DEFAULT_GET_UPDATES_TIMEOUT",
    "StringEnum",
    "DefaultEvent",
    "UpdateType",
    "APIEndpoint",
    "InputMediaType",
    "ChatType",
    "ChatMemberStatus",
    "ChatAction",
    "TransactionStatus",
    "CooldownTarget",
    "ConversationFlowTarget",
)


BALE_BASE_URL: Final[str] = "https://ble.ir"
BALE_API_BASE_URL: Final[str] = "https://tapi.bale.ai/bot{TOKEN}"
BALE_API_BUSINESS_URL: Final[str] = "https://tapi.bale.ai/business/bot{TOKEN}"
BALE_API_FILE_URL: Final[str] = "https://tapi.bale.ai/file/bot{TOKEN}"

DEFAULT_GET_UPDATES_TIMEOUT: Final[int] = 30


class Enum(_Enum):
    pass


class StringEnum(str, Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class DefaultEvent:
    READY = "on_ready"
    ":obj:`str`: Shows `on_ready <events.html#on_ready>`_ event."
    UPDATE = "on_update"
    ":obj:`str`: Shows `on_update <events.html#on_update>`_ event."
    RAW_UPDATE = "on_raw_update"
    ":obj:`str`: Shows `on_raw_update <events.html#on_raw_update>`_ event."
    HANDLER_ERROR = "on_handler_error"
    ":obj:`str`: Shows `on_handler_error <events.html#on_handler_error>`_ event."
    EVENT_ERROR = "on_event_error"
    ":obj:`str`: Shows `on_event_error <events.html#on_event_error>`_ event."
    UPDATER_READY = "on_updater_ready"
    ":obj:`str`: Shows `on_updater_ready <events.html#on_updater_ready>`_ event."
    MIDDLEWARE_ERROR = "on_middleware_process_error"
    ":obj:`str`: Shows `on_middleware_process_error <events.html#on_middleware_process_error>`_ event."


class UpdateType(StringEnum):
    CALLBACK_QUERY = "callback_query"
    ":obj:`str`: Shows :class:`~bale.Update` has :attr:`~bale.Update.callback_query` attribute."
    MESSAGE = "message"
    ":obj:`str`: Shows :class:`~bale.Update` has :attr:`~bale.Update.message` attribute."
    EDITED_MESSAGE = "edited_message"
    ":obj:`str`: Shows :class:`~bale.Update` has :attr:`~bale.Update.edited_message` attribute."


class APIEndpoint(Enum):
    GET_ME = "GET", "/getMe"
    SET_WEBHOOK = "POST", "/setWebhook"
    DELETE_WEBHOOK = "GET", "/deleteWebhook"
    SEND_MESSAGE = "POST", "/sendMessage"
    FORWARD_MESSAGE = "POST", "/forwardMessage"
    SEND_DOCUMENT = "POST", "/sendDocument"
    SEND_PHOTO = "POST", "/sendPhoto"
    SEND_AUDIO = "POST", "/sendAudio"
    SEND_VOICE = "POST", "/sendVoice"
    SEND_VIDEO = "POST", "/sendVideo"
    SEND_ANIMATION = "POST", "/sendAnimation"
    SEND_MEDIA_GROUP = "POST", "/sendMediaGroup"
    SEND_LOCATION = "POST", "/sendLocation"
    SEND_CONTACT = "POST", "/sendContact"
    SEND_INVOICE = "POST", "/sendInvoice"
    SEND_STICKER = "POST", "/sendSticker"
    SEND_CHAT_ACTION = "POST", "/sendChatAction"
    EDIT_MESSAGE_TEXT = "POST", "/editMessageText"
    EDIT_MESSAGE_CAPTION = "POST", "/editMessageCaption"
    EDIT_MESSAGE_REPLY_MARKUP = "POST", "/editMessageReplyMarkup"
    COPY_MESSAGE = "POST", "/copyMessage"
    DELETE_MESSAGE = "GET", "/deleteMessage"
    GET_CHAT = "POST", "/getChat"
    PROMOTE_CHAT_MEMBER = "POST", "/promoteChatMember"
    GET_CHAT_MEMBER = "POST", "/getChatMember"
    BAN_CHAT_MEMBER = "POST", "/banChatMember"
    UNBAN_CHAT_MEMBER = "POST", "/unbanChatMember"
    SET_CHAT_PHOTO = "POST", "/setChatPhoto"
    DELETE_CHAT_PHOTO = "POST", "/deleteChatPhoto"
    PIN_CHAT_MESSAGE = "POST", "/pinChatMessage"
    UNPIN_CHAT_MESSAGE = "POST", "/unpinChatMessage"
    UNPIN_ALL_CHAT_MESSAGES = "POST", "/unpinAllChatMessages"
    SET_CHAT_TITLE = "POST", "/setChatTitle"
    SET_CHAT_DESCRIPTION = "POST", "/setChatDescription"
    ANSWER_CALLBACK_QUERY = "POST", "/answerCallbackQuery"
    ANSWER_PRE_CHECKOUT_QUERY = "POST", "/answerPreCheckoutQuery"
    ASK_REVIEW = "POST", "/askReview"
    GET_CHAT_MEMBERS_COUNT = "GET", "/getChatMembersCount"
    GET_CHAT_MEMBERS = "GET", "/getChatMembers"
    GET_CHAT_ADMINISTRATORS = "GET", "/getChatAdministrators"
    INVITE_USER = "GET", "/inviteUser"
    REVOKE_CHAT_INVITE_LINK = "POST", "/revokeChatInviteLink"
    CREATE_CHAT_INVITE_LINK = "POST", "/createChatInviteLink"
    EXPORT_CHAT_INVITE_LINK = "POST", "/exportChatInviteLink"
    LEAVE_CHAT = "GET", "/leaveChat"
    CREATE_INVOICE_LINK = "POST", "/createInvoiceLink"
    INQUIRE_TRANSACTION = "POST", "/inquireTransaction"
    GET_WEBHOOK_INFO = "GET", "/getWebhookInfo"
    GET_UPDATES = "POST", "/getUpdates"

    @property
    def method(self) -> str:
        return self.value[0]

    @property
    def path(self) -> str:
        return self.value[1]

    def __iter__(self) -> Iterator[str]:
        return iter(self.value)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}: {self.method} {self.path}>"


class InputMediaType(StringEnum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    ANIMATION = "animation"
    DOCUMENT = "document"


class ChatType(StringEnum):
    PRIVATE = "private"
    ":obj:`str`: Shows :class:`~bale.Chat` type is private."
    GROUP = "group"
    ":obj:`str`: Shows :class:`~bale.Chat` type is group."
    CHANNEL = "channel"
    ":obj:`str`: Shows :class:`~bale.Chat` type is channel."


class ChatMemberStatus(StringEnum):
    CREATOR = "creator"
    ":obj:`str`: Shows status of chat member is create/owner."
    ADMIN = "administrator"
    ":obj:`str`: Shows status of chat member is administrator."
    MEMBER = "member"
    ":obj:`str`: Shows status of chat member is normal member."
    OWNER = CREATOR
    ":obj:`str`: An alias for :attr:`CREATOR`."


class ChatAction(StringEnum):
    TYPING = "typing"
    ":obj:`str`: Shows that the action is 'bot is typing.'"
    CHOOSE_STICKER = "choose_sticker"
    ":obj:`str`: Shows that the action is 'bot is selecting a sticker.'"
    RECORD_VIDEO = "record_video"
    ":obj:`str`: Shows that the action is 'bot is recording a video.'"
    RECORD_VOICE = "record_voice"
    ":obj:`str`: Shows that the action is 'bot is recording a voice.'"
    UPLOAD_PHOTO = "upload_photo"
    ":obj:`str`: Shows that the action is 'bot is uploading a photo.'"
    UPLOAD_VIDEO = "upload_video"
    ":obj:`str`: Shows that the action is 'bot is uploading a video.'"
    UPLOAD_VOICE = "upload_voice"
    ":obj:`str`: Shows that the action is 'bot is uploading a voice.'"


class KeyboardButtonStyle(StringEnum):
    PRIMARY = "primary"
    ":obj:`str`: Shows keyboard button style is primary (usually blue)."
    BLUE = PRIMARY
    ":obj:`str`: An alias for :attr:`PRIMARY`."
    SUCCESS = "success"
    ":obj:`str`: Shows keyboard button style is success (usually green)."
    GREEN = SUCCESS
    ":obj:`str`: An alias for :attr:`SUCCESS`."
    DANGER = "danger"
    ":obj:`str`: Shows keyboard button style is danger (usually red)."
    RED = DANGER
    ":obj:`str`: An alias for :attr:`DANGER`."


class TransactionStatus(StringEnum):
    PENDING = "pending"
    ":obj:`str`: The transaction is in progress and awaiting processing."
    SUCCEED = "succeed"
    ":obj:`str`: The transaction completed successfully."
    FAILED = "failed"
    ":obj:`str`: The transaction failed due to an error or rejection from the system."
    REJECTED = "rejected"
    ":obj:`str`: The bot explicitly rejected the transaction request."
    TIMEOUT = "timeout"
    ":obj:`str`: The bot did not confirm the transaction within the allowed time period."


class CooldownTarget(Enum):
    """
    .. list-table::
       :widths: 20 60 60
       :header-rows: 1
       :align: center

       * - Target
         - How the Limitation Works
         - Example (Only the Target Differs)
       * - User
         - This limitation is based on the user's unique identifier.
         - Each user can use the specified handler only twice every 20 seconds.
       * - Chat
         - This limitation is based on the unique identifier of the chat.
         - In each chat, the specified handler can be used only twice every 20 seconds.
       * - Chat Member
         - This limitation is based on a combination of the user's unique identifier and the chat identifier. Together, they form a single key.
         - Each chat member can use the specified handler only twice every 20 seconds.
    """

    USER = 1
    "This limitation is based on the user's unique identifier."
    CHAT_MEMBER = 2
    "This limitation is based on a combination of the user's unique identifier and the chat identifier. Together, they form a single key."
    CHAT = 3
    "This limitation is based on the unique identifier of the chat."

    def __call__(self, context: "Context") -> Any:
        if self is CooldownTarget.USER:
            return context.user_id
        if self is CooldownTarget.CHAT_MEMBER:
            return context.chat_id, context.user_id
        if self is CooldownTarget.CHAT:
            return context.chat_id

        raise AssertionError(f"Unhandled ConversationFlowTarget: {self!r}")


class ConversationFlowTarget(Enum):
    """
    .. list-table::
       :widths: 20 60 60
       :header-rows: 1
       :align: center

       * - Target
         - How the Limitation Works
         - Example (Only the Target Differs)
       * - User
         - This limitation is based on the user's unique identifier.
         - Each user can use the specified handler only twice every 20 seconds.
       * - Chat
         - This limitation is based on the unique identifier of the chat.
         - In each chat, the specified handler can be used only twice every 20 seconds.
       * - Chat Member
         - This limitation is based on a combination of the user's unique identifier and the chat identifier. Together, they form a single key.
         - Each chat member can use the specified handler only twice every 20 seconds.
    """

    USER = 1
    "This limitation is based on the user's unique identifier."
    CHAT_MEMBER = 2
    "This limitation is based on a combination of the user's unique identifier and the chat identifier. Together, they form a single key."
    CHAT = 3
    "This limitation is based on the unique identifier of the chat."

    def __call__(self, context: "Context") -> Hashable | tuple[Hashable, Hashable]:
        if self is ConversationFlowTarget.USER:
            return context.user_id
        if self is ConversationFlowTarget.CHAT_MEMBER:
            return context.chat_id, context.user_id
        if self is ConversationFlowTarget.CHAT:
            return context.chat_id

        raise AssertionError(f"Unhandled ConversationFlowTarget: {self!r}")
